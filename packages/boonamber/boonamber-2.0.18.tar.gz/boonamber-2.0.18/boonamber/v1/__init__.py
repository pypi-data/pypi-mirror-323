import base64
import itertools
import numpy as np
import json
import gzip
import os
import time
import requests
import urllib3
from collections.abc import Iterable
from numbers import Number, Integral
from ..util.ambererror import AmberCloudError as ace, AmberUserError as aue

from urllib3.exceptions import InsecureRequestWarning


############################
# Boon Amber Python SDK v1 #
############################


class AmberCloudError(ace):
    pass


class AmberUserError(aue):
    pass


class AmberV1Client:
    def __init__(
        self,
        license_id="default",
        license_file="~/.Amber.license",
        verify=True,
        cert=None,
        timeout=300,
    ):
        """Main client which interfaces with the Amber cloud. Amber account
        credentials are discovered within a .Amber.license file located in the
        home directory, or optionally overridden using environment variables.

        Args:
            license_id (str): license identifier label found within .Amber.license file
            license_file (str): path to .Amber.license file
            verify:  Boolean, controls whether we verify the server’s TLS certificate
            cert (bool): if String, path to ssl client cert file (.pem). If Tuple, (‘cert’, ‘key’) pair.

        Environment:

            `AMBER_LICENSE_FILE`: sets license_file path

            `AMBER_LICENSE_ID`: sets license_id

            `AMBER_USERNAME`: overrides the username as found in .Amber.license file

            `AMBER_PASSWORD`: overrides the password as found in .Amber.license file

            `AMBER_SERVER`: overrides the server as found in .Amber.license file

            `AMBER_OAUTH_SERVER`: overrides the oauth server as found in .Amber.license file

            `AMBER_SSL_CERT`: path to ssl client cert file (.pem)

            `AMBER_SSL_VERIFY`: Either a boolean, in which case it controls whether we verify the server’s TLS certificate, or a string, in which case it must be a path to a CA bundle to use

        Raises:
            AmberUserError: if error supplying authentication credentials
        """

        self.token = None
        self.reauth_time = 0
        self.user_agent = "Boon Logic / amber-python-sdk / requests"
        self.timeout = timeout

        # first load from license file, override from environment if specified
        self.license_file = license_file
        self.license_file = os.environ.get("AMBER_LICENSE_FILE", self.license_file)

        # Server type identification.  "basic" or "aws"
        self.server_type = None

        # determine which license_id to use, override from environment if specified
        self.license_id = os.environ.get("AMBER_LICENSE_ID", license_id)

        # TODO allow non existant license file and license id only if username/password/server are set in environ
        # create license profile
        if self.license_file is not None:
            license_path = os.path.expanduser(self.license_file)
            if not os.path.exists(license_path):
                self.license_profile = json.loads('{"username": "", "password": "", "server": "", "oauth-server": ""}')
            else:
                try:
                    with open(license_path, "r") as f:
                        file_data = json.load(f)
                except json.JSONDecodeError as e:
                    raise AmberUserError("JSON formatting error in license file: {}, line: {}, col: {}".format(e.msg, e.lineno, e.colno))
                try:
                    self.license_profile = file_data[self.license_id]
                except KeyError:
                    raise AmberUserError('license_id "{}" not found in license file'.format(self.license_id))
        else:
            # no license file found, create a stub profile to be filled in from environment
            self.license_profile = json.loads('{"username": "", "password": "", "server": "", "oauth-server": ""}')

        # override from environment if specified
        try:
            self.license_profile["username"] = os.environ.get("AMBER_USERNAME", self.license_profile["username"])
            self.license_profile["password"] = os.environ.get("AMBER_PASSWORD", self.license_profile["password"])
            self.license_profile["server"] = os.environ.get("AMBER_SERVER", self.license_profile["server"])
            if "oauth-server" not in self.license_profile or not self.license_profile:
                self.license_profile["oauth-server"] = self.license_profile["server"]
            self.license_profile["oauth-server"] = os.environ.get("AMBER_OAUTH_SERVER", self.license_profile["oauth-server"])
            if self.license_profile["oauth-server"] == "":
                self.license_profile["oauth-server"] = self.license_profile["server"]
            self.license_profile["cert"] = os.environ.get("AMBER_SSL_CERT", cert)
            verify_str = os.environ.get("AMBER_SSL_VERIFY", "true").lower()
            self.license_profile["verify"] = True  # Default
            if not verify or verify_str == "false":
                self.license_profile["verify"] = False
        except KeyError as e:
            raise AmberUserError("missing field")

        if self.license_profile["verify"] is False:
            urllib3.disable_warnings(category=InsecureRequestWarning)

        # verify required profile elements have been created
        if self.license_profile["username"] == "":
            raise AmberUserError('username "{}" not specified'.format(self.license_profile["username"]))
        if self.license_profile["password"] == "":
            raise AmberUserError('password "{}" not specified'.format(self.license_profile["password"]))
        if self.license_profile["server"] == "":
            raise AmberUserError('server "{}" not specified'.format(self.license_profile["server"]))

    def _authenticate(self):
        """Authenticate client for the next hour using the credentials given at
        initialization. This acquires and stores an oauth2 token which remains
        valid for one hour and is used to authenticate all other API requests.

        Raises:
            AmberCloudError: if Amber cloud gives non-200 response
        """

        url = self.license_profile["oauth-server"] + "/oauth2"
        headers = {"Content-Type": "application/json", "User-Agent": self.user_agent}
        body = {
            "username": self.license_profile["username"],
            "password": self.license_profile["password"],
        }

        try:
            response = requests.request(
                method="POST",
                url=url,
                headers=headers,
                json=body,
                verify=self.license_profile["verify"],
                cert=self.license_profile["cert"],
                timeout=self.timeout,
            )

            if response.status_code != 200:
                message = "authentication failed: {}".format(response.json().get("message", "no message"))
                raise AmberCloudError(response.status_code, message)

            # establish server_type if not identified
            if self.server_type is None:
                if response.headers.get("x-amz-apigw-id") is not None:
                    self.server_type = "aws"
                else:
                    self.server_type = "basic"

            # invalid credentials return a 200 where token is an empty string
            self.token = response.json().get("idToken")
            if self.token is None:
                raise AmberCloudError(401, "authentication failed: invalid credentials")

            expire_secs = int(response.json().get("expiresIn"))
            if expire_secs is None:
                raise AmberCloudError(401, "authentication failed: missing expiration")
            self.reauth_time = time.time() + expire_secs - 60

        except requests.exceptions.Timeout:
            raise AmberCloudError(500, "request timed out")
        except Exception:
            raise AmberCloudError(401, "invalid server connection")

    def _api_call(self, method, url, headers, body=None):
        """Make a REST call to the Amber server and handle the response"""

        if time.time() > self.reauth_time:
            self._authenticate()

        headers["Authorization"] = "Bearer {}".format(self.token)
        headers["User-Agent"] = self.user_agent
        headers["Content-Type"] = "application/json"

        impersonate = os.environ.get("AMBER_IMPERSONATE", "")
        if impersonate != "":
            headers["impersonate"] = impersonate

        body = json.dumps(body)

        if method == "POST" and len(body) > 10000:
            headers["content-encoding"] = "gzip"
            body = gzip.compress(body.encode("utf-8"))

        try:
            response = requests.request(
                method=method,
                url=url,
                headers=headers,
                data=body,
                verify=self.license_profile["verify"],
                cert=self.license_profile["cert"],
                timeout=self.timeout,
            )
        except requests.exceptions.Timeout:
            # request timed out
            raise AmberCloudError(500, "request timed out")
        except requests.exceptions.ConnectionError:
            raise AmberCloudError(500, "server does not exist")

        if response.status_code > 299:
            try:
                msg = response.json()
                try:
                    msg = msg.get("message", "no message")
                except AttributeError:
                    pass
            except json.JSONDecodeError:
                msg = response.text
            raise AmberCloudError(response.status_code, msg)

        try:
            respbody = response.json()
        except json.JSONDecodeError:
            msg = response.text
            raise AmberCloudError(response.status_code, f"could not decode response as JSON: '{msg}'")

        # if code is returned in the message, it should agree with the header
        if "code" in respbody and respbody["code"] != response.status_code:
            raise AmberCloudError(respbody["code"], respbody.get("message", "no message"))

        if "errorMessage" in respbody:
            raise AmberCloudError(500, respbody["errorMessage"])

        return response

    def get_summary(self, sensor_id):
        """Get summary information for a sensor

        Returns:
            json summary information

        Raises:
            AmberCloudError: if Amber cloud gives non-200 response
        """

        url = self.license_profile["server"] + "/__summary"
        headers = {"Content-Type": "application/json", "sensorId": sensor_id}
        response = self._api_call("GET", url, headers)

        return response.json()

    def get_version(self):
        """Get version information for Amber

        Returns:
            json version information

        Raises:
            AmberCloudError: if Amber cloud gives non-200 response
        """

        url = self.license_profile["server"] + "/version"
        headers = {"Content-Type": "application/json"}
        response = self._api_call("GET", url, headers)

        return response.json()

    def create_sensor(self, label=""):
        """Create a new sensor instance

        Args:
            label (str): label to assign to created sensor

        Returns:
            A string containing the `sensor_id` that was created

        Raises:
            AmberUserError: if client is not authenticated
            AmberCloudError: if Amber cloud gives non-200 response
        """

        url = self.license_profile["server"] + "/sensor"
        headers = {"Content-Type": "application/json"}
        body = {"label": label}
        response = self._api_call("POST", url, headers, body=body)
        sensor_id = response.json()["sensorId"]

        return sensor_id

    def update_label(self, sensor_id, label):
        """Update the label of a sensor instance

        Args:
            sensor_id (str): sensor identifier
            label (str): new label to assign to sensor

        Returns:
            A string containing the new label assigned to sensor

        Raises:
            AmberUserError: if client is not authenticated
            AmberCloudError: if Amber cloud gives non-200 response
        """

        url = self.license_profile["server"] + "/sensor"
        headers = {"Content-Type": "application/json", "sensorId": sensor_id}
        body = {"label": label}
        response = self._api_call("PUT", url, headers, body=body)
        label = response.json()["label"]

        return label

    def delete_sensor(self, sensor_id):
        """Delete an amber sensor instance

        Args:
            sensor_id (str): sensor identifier

        Raises:
            AmberUserError: if client is not authenticated
            AmberCloudError: if Amber cloud gives non-200 response
        """

        url = self.license_profile["server"] + "/sensor"
        headers = {"Content-Type": "application/json", "sensorId": sensor_id}
        response = self._api_call("DELETE", url, headers)
        return response.json()

    def list_sensors(self):
        """List all sensor instances currently associated with Amber account

        Returns:
            A dictionary mapping sensor IDs to corresponding labels

        Raises:
            AmberUserError: if client is not authenticated
            AmberCloudError: if Amber cloud gives non-200 response
        """

        url = self.license_profile["server"] + "/sensors"
        headers = {"Content-Type": "application/json"}
        response = self._api_call("GET", url, headers)
        sensors = {s["sensorId"]: s.get("label", None) for s in response.json()}

        return sensors

    def post_outage(self, sensor_id):
        url = self.license_profile["server"] + "/outage"
        headers = {"Content-Type": "application/json", "sensorId": sensor_id}
        response = self._api_call("POST", url, headers)
        return response.json()

    def configure_sensor(
        self,
        sensor_id,
        feature_count=1,
        streaming_window_size=25,
        samples_to_buffer=10000,
        anomaly_history_window=10000,
        learning_rate_numerator=10,
        learning_rate_denominator=10000,
        learning_max_clusters=1000,
        learning_max_samples=1000000,
        features=None,
        override_pv=None,
    ):
        """Configure an amber sensor instance

        Args:
            sensor_id (str): sensor identifier
            feature_count (int): number of features (dimensionality of each data sample)
            streaming_window_size (int): streaming window size (number of samples)
            samples_to_buffer (int): number of samples to load before autotuning
            anomaly_history_window (int): number of samples to use for AH calculation
            learning_rate_numerator (int): sensor "graduates" (i.e. transitions from
                learning to monitoring mode) if fewer than learning_rate_numerator
                new clusters are opened in the last learning_rate_denominator samples
            learning_rate_denominator (int): see learning_rate_numerator
            learning_max_clusters (int): sensor graduates if this many clusters are created
            learning_max_samples (int): sensor graduates if this many samples are processed
            features (list): optional list of per feature settings (minVal, maxVal, and label)
            override_pv (float): force percent variation to specific value

        Returns:
            A dictionary containing:

                {
                    'feature_count': int,
                    'streaming_window_size': int,
                    'samples_to_buffer': int
                    'anomaly_history_window': int,
                    'learning_rate_numerator': int,
                    'learning_rate_denominator': int,
                    'learning_max_clusters': int,
                    'learning_max_samples': int,
                    'features': [
                        {
                            'minVal': float,
                            'maxVal': float,
                            'label': string,
                            'weight': float,
                            'submitRule': string
                        },
                        ...
                    ]
                }

        Raises:
            AmberUserError: if client is not authenticated or supplies invalid options
            AmberCloudError: if Amber cloud gives non-200 response
        """
        if features is None:
            features = []

        if not feature_count > 0 or not isinstance(feature_count, Integral):
            raise AmberUserError("invalid 'feature_count': must be positive integer")

        if not streaming_window_size > 0 or not isinstance(streaming_window_size, Integral):
            raise AmberUserError("invalid 'streaming_window_size': must be positive integer")

        url = self.license_profile["server"] + "/config"
        headers = {"Content-Type": "application/json", "sensorId": sensor_id}
        body = {
            "featureCount": feature_count,
            "streamingWindowSize": streaming_window_size,
            "samplesToBuffer": samples_to_buffer,
            "anomalyHistoryWindow": anomaly_history_window,
            "learningRateNumerator": learning_rate_numerator,
            "learningRateDenominator": learning_rate_denominator,
            "learningMaxClusters": learning_max_clusters,
            "learningMaxSamples": learning_max_samples,
            "features": features,
        }
        if override_pv is not None:
            body["percentVariationOverride"] = override_pv
        config = self._api_call("POST", url, headers, body=body)

        return config.json()

    def configure_fusion(self, sensor_id, feature_count=5, features=None):
        """Configure an Amber instance for sensor fusion

        Args:
            sensor_id (str): sensor identifier
            feature_count (int): number of features or data streams to fuse together
            features (list): optional list of per feature settings overriding feature_count.
                Allows direct setting of feature labels and rules for submitting the fusion vector:
                [
                    {
                        'label': string,
                        'submitRule': string (one of: 'submit', 'nosubmit')
                    },
                    ...
                ]

        Returns:
            A list of features as configured

        Raises:
            AmberUserError: if client is not authenticated or supplies invalid data
            AmberCloudError: if Amber cloud gives non-200 response.
        """
        if not features:
            if not feature_count > 0 or not isinstance(feature_count, Integral):
                raise AmberUserError("invalid 'feature_count': must be positive integer")
            for i in range(feature_count):
                features.append(
                    {
                        "label": "",  # allow server to fill in default values
                        "submitRule": "",
                    }
                )

        url = self.license_profile["server"] + "/config"
        headers = {"Content-Type": "application/json", "sensorId": sensor_id}
        body = {"features": features}
        response = self._api_call("PUT", url, headers, body=body)
        return response.json()["features"]

    def enable_learning(
        self,
        sensor_id,
        learning_rate_numerator=None,
        learning_rate_denominator=None,
        learning_max_clusters=None,
        learning_max_samples=None,
    ):
        """Enable learning for a sensor thats in monitoring state


        Args:
            sensor_id (str): sensor identifier
            learning_rate_numerator (int): number of new clusters created as a max before turning off learning
            learning_rate_denominator (int): number of recent inferences to count the number of new clusters over
            learning_max_clusters (int): maximum number of clusters allowed to be created
            learning_max_samples (int): maximum number of samples to process in learning

        Returns:

            {
                'learning_rate_numerator': int,
                'learning_rate_denominator': int,
                'learning_max_clusters': int,
                'learning_max_samples': int
            }

        Raises:
            AmberUserError: if client is not authenticated or supplies invalid data
            AmberCloudError: if Amber cloud gives non-200 response
        """

        # Server expects data as a plaintext string of comma-separated values.

        streaming = {}
        if learning_rate_numerator:
            streaming["learningRateNumerator"] = learning_rate_numerator
        if learning_rate_denominator:
            streaming["learningRateDenominator"] = learning_rate_denominator
        if learning_max_samples:
            streaming["learningMaxSamples"] = learning_max_samples
        if learning_max_clusters:
            streaming["learningMaxClusters"] = learning_max_clusters

        url = self.license_profile["server"] + "/config"
        headers = {"Content-Type": "application/json", "sensorId": sensor_id}
        body = {"streaming": streaming}
        response = self._api_call("PUT", url, headers, body=body)
        return response.json()["streaming"]

    def pretrain_sensor(self, sensor_id, data, autotune_config=True, block=True):
        """Pretrain a sensor with historical data

        Args:
            sensor_id (str): sensor identifier
            data (array-like): data to be inferenced. Must be non-empty,
                entirely numeric and one of the following: scalar value,
                list-like or list-of-lists-like where all sublists have
                equal length.
            autotune_config (bool): if True, the sensor will be reconfigured based
                on the training data provided so that the sensor will be in monitoring
                once the data is through. If False, the sensor uses the already
                configured values to train the sensor.
            block (bool): if True, will block until pretraining is complete.
                Otherwise, will return immediately; in this case pretraining
                status can be checked using get_pretrain_state endpoint.

        Returns:

            {
                'state': str
            }

            'state': current state of the sensor.
                "Pretraining": pretraining is in progress

        Raises:
            AmberUserError: if client is not authenticated or supplies invalid data
            AmberCloudError: if Amber cloud gives non-200 response
        """

        # Server expects data as a plaintext string of comma-separated values.
        try:
            data_csv = float_list_to_csv_string(data)
        except ValueError as e:
            raise AmberUserError("invalid data: {}".format(e))

        url = self.license_profile["server"] + "/pretrain"
        headers = {"Content-Type": "application/json", "sensorId": sensor_id}
        body = {"data": data_csv, "autotuneConfig": autotune_config}

        results = self._api_call("POST", url, headers, body=body)

        if not block:
            return results.json()

        while True:
            results = self.get_pretrain_state(sensor_id)
            if results["state"] == "Pretraining":
                time.sleep(5)
                continue
            else:
                return results

    def pretrain_sensor_xl(self, sensor_id, data, autotune_config=True, block=True, chunk_size=4000000):
        """Pretrain a sensor with extra large sets of historical data.

        Args:
            sensor_id (str): sensor identifier
            data (array-like): data to be inferenced. Must be non-empty,
                entirely numeric and one of the following: scalar value,
                list-like or list-of-lists-like where all sublists have
                equal length.
            autotune_config (bool): if True, the sensor will be reconfigured based
                on the training data provided so that the sensor will be in monitoring
                once the data is through. If False, the sensor uses the already
                configured values to train the sensor.
            block (bool): if True, will block until pretraining is complete.
                Otherwise, will return immediately; in this case pretraining
                status can be checked using get_pretrain_state endpoint.

        Returns:

            {
                'state': str
            }

            'state': current state of the sensor.
                "Pretraining": pretraining is in progress

        Raises:
            AmberUserError: if client is not authenticated or supplies invalid data
            AmberCloudError: if Amber cloud gives non-200 response
        """

        # Server expects data as a plaintext string of comma-separated values.
        try:
            data = packed_floats(data)
        except ValueError as e:
            raise AmberUserError("invalid data: {}".format(e))

        url = self.license_profile["server"] + "/pretrain"
        headers = {"content-type": "application/octet-stream", "sensorId": sensor_id}
        body = {"data": "", "format": "packed-float", "autotuneConfig": autotune_config}

        # chunk size is set at 4MB (1 million floats * 4 bytes)
        if chunk_size > 4000000:
            raise AmberCloudError(400, "chunk_size must be <= 4000000")

        # compute number of chunks to send
        num_chunks = int(len(data) / chunk_size)
        if len(data) % chunk_size != 0:
            num_chunks += 1

        amber_transaction = None
        response = None
        for chunk_num in range(0, num_chunks):
            # include amberChunk header designation, .ie 1:3, 2:3, 3:3
            headers["amberchunk"] = "{}:{}".format(chunk_num + 1, num_chunks)
            if amber_transaction is not None:
                headers["ambertransaction"] = amber_transaction

            # compute start and end range of next chunk
            start = chunk_num * chunk_size
            end = start + chunk_size
            if end > len(data):
                end = len(data)

            body["data"] = base64.b64encode(data[start:end]).decode("ascii")
            response = self._api_call("POST", url, headers, body=body)
            if "ambertransaction" in response.headers:
                amber_transaction = response.headers["ambertransaction"]

        if not block:
            return response.json()

        while True:
            results = self.get_pretrain_state(sensor_id)
            if results["state"] == "Pretraining":
                time.sleep(5)
                continue
            else:
                return results

    def get_pretrain_state(self, sensor_id):
        """Gets the state of sensor that is being pretrained

        Args:
            sensor_id (str): sensor identifier

        Returns:

            {
                    'state': str
            }

            'state': current state of the sensor. One of:
                "Pretraining": pretraining is in progress
                "Pretrained": pretraining has completed
                "Error": error has occurred
        Raises:
            AmberUserError: if client is not authenticated or supplies invalid data
            AmberCloudError: if Amber cloud gives non-200 response
        """

        url = self.license_profile["server"] + "/pretrain"
        headers = {"Content-Type": "application/json", "sensorId": sensor_id}

        response = self._api_call("GET", url, headers)
        return response.json()

    def stream_fusion(self, sensor_id, vector, submit=None):
        """Stream data to a fusion-configured sensor

        Args:
            sensor_id (str): sensor identifier
            vector (list of dict): list of one or more dictionaries, each
                giving an updated value for one of the sensor fusion features:
                [
                    {
                        "label": str,
                        "value": float,
                    },
                    ...
                ]
            submit (bool or None): whether to submit the fusion vector after this update.
                If None, whether to submit will be determined by the per-feature submit rules.

        Returns:
            - When no analytics were generated: A Dict containing current sample vector
            {
                "vector": "sample, sample, sample, ...",
            }

            - When analytics were generated: A Dict containing both the current sample vector and results
            {
                "vector": "sample, sample, sample, ...",
                "results": {
                    'state': str,
                    'message': str,
                    'progress': int,
                    'clusterCount': int,
                    'retryCount': int,
                    'streamingWindowSize': int,
                    'totalInferences': int,
                    'lastModified': 'int',
                    'lastModifiedDelta': 'int',
                    'ID': [int],
                    'SI': [int],
                    'AD': [int],
                    'AH': [int],
                    'AM': [float],
                    'AW': [int],
                    'NI': [int],
                    'NS': [int],
                    'NW': [float],
                    'OM': [float]
                }
            }

        Raises:
            AmberUserError: if client is not authenticated or supplies invalid data
            AmberCloudError: if Amber cloud gives non-200 response.
        """
        sopts = ["submit", "nosubmit", "default"]
        if submit is None:
            submit = "default"
        if submit not in sopts:
            raise ValueError("'submit' must be one of {}, got {}".format(sopts, submit))

        url = self.license_profile["server"] + "/stream"
        headers = {"Content-Type": "application/json", "sensorId": sensor_id}
        body = {"vector": vector, "submitRule": submit}
        response = self._api_call("PUT", url, headers, body=body)
        return response.json()

    def stream_sensor(self, sensor_id, data, save_image=True):
        """Stream data to an amber sensor and return the inference result

        Args:
            sensor_id (str): sensor identifier
            data (array-like): data to be inferenced. Must be non-empty,
                entirely numeric and one of the following: scalar value,
                list-like or list-of-lists-like where all sublists have
                equal length.
            save_image (bool): whether to save the image after calculation

        Returns:
            A dictionary containing inferencing results:

                {
                    'state': str,
                    'message': str,
                    'progress': int,
                    'clusterCount': int,
                    'retryCount': int,
                    'streamingWindowSize': int,
                    'totalInferences': int,
                    'lastModified': 'int',
                    'lastModifiedDelta': 'int',
                    'ID': [int],
                    'SI': [int],
                    'AD': [int],
                    'AH': [int],
                    'AM': [float],
                    'AW': [int],
                    'NI': [int],
                    'NS': [int],
                    'NW': [float],
                    'OM': [float]
                }

                'state': current state of the sensor. One of:
                    "Buffering": gathering initial sensor data
                    "Autotuning": autotuning configuration in progress
                    "Learning": sensor is active and learning
                    "Monitoring": sensor is active but monitoring only (learning disabled)
                    "Error": fatal error has occurred
                'message': accompanying message for current sensor state
                'progress' progress as a percentage value (applicable for "Buffering" and "Autotuning" states)
                'clusterCount' number of clusters created so far
                'retryCount' number of times autotuning was re-attempted to tune streamingWindowSize
                'streamingWindowSize': streaming window size of sensor (may differ from value
                    given at configuration if window size was adjusted during autotune)
                'totalInferences': number of inferences since configuration
                'lastModified': current Unix timestamp when the call was made
                'lastModifiedDelta': number of seconds since the last stream call
                'ID': list of cluster IDs. The values in this list correspond one-to-one
                    with input samples, indicating the cluster to which each input pattern
                    was assigned.
                'SI': smoothed anomaly index. The values in this list correspond
                    one-for-one with input samples and range between 0 and 1000. Values
                    closer to 0 represent input patterns which are ordinary given the data
                    seen so far on this sensor. Values closer to 1000 represent novel patterns
                    which are anomalous with respect to data seen before.
                'RI': raw anomaly index. These values are the SI values without any smoothing.
                'AD': list of binary anomaly detection values. These correspond one-to-one
                    with input samples and are produced by thresholding the smoothed anomaly
                    index (SI). The threshold is determined automatically from the SI values.
                    A value of 0 indicates that the SI has not exceeded the anomaly detection
                    threshold. A value of 1 indicates it has, signaling an anomaly at the
                    corresponding input sample.
                'AH': list of anomaly history values. These values are a moving-window sum of
                    the AD value, giving the number of anomaly detections (1's) present in the
                    AD signal over a "recent history" window whose length is the buffer size.
                'AM': list of "Amber Metric" values. These are floating point values between
                    0.0 and 1.0 indicating the extent to which each corresponding AH value
                    shows an unusually high number of anomalies in recent history. The values
                    are derived statistically from a Poisson model, with values close to 0.0
                    signaling a lower, and values close to 1.0 signaling a higher, frequency
                    of anomalies than usual.
                'AW': list of "Amber Warning Level" values. This index is produced by thresholding
                    the Amber Metric (AM) and takes on the values 0, 1 or 2 representing a discrete
                    "warning level" for an asset based on the frequency of anomalies within recent
                    history. 0 = normal, 1 = asset changing, 2 = asset critical. The default
                    thresholds for the two warning levels are the standard statistical values
                    of 0.95 (outlier, asset changing) and 0.997 (extreme outlier, asset critical).
                'NI': list of "Novelty Index" values. These are values that show how different a new
                    cluster actually is from the model. If the cluster is already in the model, it
                    returns a 0. New clusters return an RI type value ranging from 0 to 1000 based on
                    the L2 distance it is from the model's clusters.
                'NS': list of "Smoothed Novelty Index" values. This is just a weighted average of the
                    new NI and the previous NI. These values range from 0 to 1000..
                'NW': list of "Novelty Warning Level" values. This is just a scaled version of the NS
                    values that now range from 0 to 2 to give a warning level for the asset.
                'OM': list of operational mode values that are a sliding average of the cluster IDs
                    to give a basic representation of the different states

        Raises:
            AmberUserError: if client is not authenticated or supplies invalid data
            AmberCloudError: if Amber cloud gives non-200 response
        """

        # Server expects data as a plaintext string of comma-separated values.
        try:
            data_csv = float_list_to_csv_string(data)
        except ValueError as e:
            raise AmberUserError("invalid data: {}".format(e))

        url = self.license_profile["server"] + "/stream"
        headers = {"Content-Type": "application/json", "sensorId": sensor_id}
        body = {"saveImage": save_image, "data": data_csv}
        response = self._api_call("POST", url, headers, body=body)
        return response.json()

    def get_sensor(self, sensor_id):
        """Get info about a sensor

        Args:
            sensor_id (str): sensor identifier

        Returns:
            A dictionary containing sensor information:

                {
                    'label': str,
                    'sensorId': str,
                    'tenantId': str,
                    'usageInfo': {
                        putSensor {
                            'callsTotal': int
                            'callsThisPeriod': int
                            'lastCalled': str
                        },
                        getSensor {
                            'callsTotal': int
                            'callsThisPeriod': int
                            'lastCalled': str
                        },
                        getConfig {
                            'callsTotal': int
                            'callsThisPeriod': int
                            'lastCalled': str
                        },
                        postStream {
                            'callsTotal': int
                            'callsThisPeriod': int
                            'lastCalled': int
                            'samplesTotal': int
                            'samplesThisPeriod': int
                        }
                        getStatus {
                            'callsTotal': int
                            'callsThisPeriod': int
                            'lastCalled': str
                        }
                    }
                }

                'label' (str): sensor label
                'sensorId' (str): sensor identifier
                'tenantId' (str): username of associated Amber account
                'callsTotal': total number of calls to this endpoint
                'callsThisPeriod': calls this billing period to this endpoint
                'lastCalled': ISO formatted time of last call to this endpoint
                'samplesTotal': total number of samples processed
                'samplesThisPeriod': number of samples processed this billing period

        Raises:
            AmberUserError: if client is not authenticated
            AmberCloudError: if Amber cloud gives non-200 response
        """

        url = self.license_profile["server"] + "/sensor"
        headers = {"Content-Type": "application/json", "sensorId": sensor_id}
        response = self._api_call("GET", url, headers)
        return response.json()

    def get_config(self, sensor_id):
        """Get current sensor configuration

        Args:
            sensor_id (str): sensor identifier

        Returns:
            A dictionary containing the current sensor configuration:

                {
                    'featureCount': int,
                    'streamingWindowSize': int,
                    'samplesToBuffer': int,
                    'anomalyHistoryWindow': int,
                    'learningRateNumerator': int,
                    'learningRateDenominator': int,
                    'learningMaxClusters': int,
                    'learningMaxSamples': int,
                    'percentVariation': float,
                    'features':
                    [
                        {
                            'min': float,
                            'max': float
                        }
                    ]
                }

                'featureCount': number of features (dimensionality of each data sample)
                'streamingWindowSize': streaming window size (number of samples)
                'samplesToBuffer': number of samples to load before autotuning
                'anomalyHistoryWindow': number of samples to calculate normal anomaly variation
                'learningRateNumerator': sensor "graduates" (i.e. transitions from
                    learning to monitoring mode) if fewer than learning_rate_numerator
                    new clusters are opened in the last learning_rate_denominator samples
                'learningRateDenominator': see learning_rate_numerator
                'learningMaxClusters': sensor graduates if this many clusters are created
                'learningMaxSamples': sensor graduates if this many samples are processed
                'percentVariation': percent variation parameter discovered by autotuning
                'features': min/max values per feature discovered by autotuning
        Raises:
            AmberUserError: if client is not authenticated
            AmberCloudError: if Amber cloud gives non-200 response
        """

        url = self.license_profile["server"] + "/config"
        headers = {"Content-Type": "application/json", "sensorId": sensor_id}
        response = self._api_call("GET", url, headers)

        return response.json()

    def get_status(self, sensor_id):
        """Get sensor status

        Args:
            sensor_id (str): sensor identifier

        Returns:
            A dictionary containing the clustering status for a sensor:

                {
                    'pca' [(int,int,int)],
                    'clusterGrowth' [int],
                    'clusterSizes' [int],
                    'anomalyIndexes' [int],
                    'frequencyIndexes' [int],
                    'distanceIndexes' [int],
                    'totalInferences' [int],
                    'numClusters' [int],
                }

                'pca': list of length-3 vectors representing cluster centroids
                    with dimensionality reduced to 3 principal components. List length
                    is one plus the maximum cluster ID, with element 0 corresponding
                    to the "zero" cluster, element 1 corresponding to cluster ID 1, etc.
                'clusterGrowth': sample index at which each new cluster was created.
                    Elements for this and other list results are ordered as in 'pca'.
                'clusterSizes': number of samples in each cluster
                'anomalyIndexes': anomaly index associated with each cluster
                'frequencyIndexes': frequency index associated with each cluster
                'distanceIndexes': distance index associated with each cluster
                'totalInferences': total number of inferences performed so far
                'numClusters': number of clusters created so far (includes zero cluster)

        Raises:
            AmberUserError: if client is not authenticated
            AmberCloudError: if Amber cloud gives non-200 response
        """

        url = self.license_profile["server"] + "/status"
        headers = {"Content-Type": "application/json", "sensorId": sensor_id}
        response = self._api_call("GET", url, headers)

        return response.json()

    def get_root_cause(self, sensor_id, id_list=None, pattern_list=None):
        """Get root cause

        Args:
            sensor_id (str): sensor identifier
            id_list (list): list of IDs to return the root cause for
            pattern_list (list): list of pattern vectors to calculate the root cause against the model

        Returns:
            A list containing the root cause for each pattern/id provided for a sensor:

                [float]

        Raises:
            AmberUserError: if client is not authenticated
            AmberCloudError: if Amber cloud gives non-200 response
        """

        if id_list is None:
            if pattern_list is None:
                raise AmberUserError("Must specify either id_list or pattern_list for analysis")
            id_list = []
        else:
            if pattern_list is not None:
                raise AmberUserError("Cannot specify both patterns and cluster IDs for analysis")
            pattern_list = []

        url_call = "rootCause?"
        if len(id_list) != 0:
            # IDs
            id_list = [str(element) for element in id_list]
            url_call = url_call + "clusterID=[" + ",".join(id_list) + "]"
        elif len(pattern_list) != 0:
            # patterns
            if len(np.array(pattern_list).shape) == 1:  # only 1 pattern provided
                pattern_list = [pattern_list]
            else:
                for i, pattern in enumerate(pattern_list):
                    pattern_list[i] = ",".join([str(element) for element in pattern])
            url_call = url_call + "pattern=[[" + "],[".join(pattern_list) + "]]"
        else:
            raise AmberUserError("Must specify either cluster IDs or patterns to analyze")

        url = self.license_profile["server"] + "/" + url_call
        headers = {"Content-Type": "application/json", "sensorId": sensor_id}
        response = self._api_call("GET", url, headers)

        return response.json()


def validate_dims(data):
    """Validate that data is non-empty and one of the following:
    scalar value, list-like or list-of-lists-like where all
    sublists have equal length. Return 0, 1 or 2 as inferred
    number of array dimensions
    """

    # not-iterable data is a single scalar data point
    if not _isiterable(data):
        return 0

    # iterable and unnested data is a 1-d array
    if not any(_isiterable(d) for d in data):
        if len(list(data)) == 0:
            raise ValueError("empty")
        return 1

    # iterable and nested data is 2-d array
    if not all(_isiterable(d) for d in data):
        raise ValueError("cannot mix nested scalars and iterables")

    sublengths = [len(list(d)) for d in data]
    if len(set(sublengths)) > 1:
        raise ValueError("nested sublists must have equal length")

    flattened_2d = list(itertools.chain.from_iterable(data))

    if any(isinstance(i, Iterable) for i in flattened_2d):
        raise ValueError("cannot be nested deeper than list-of-lists")

    if sublengths[0] == 0:
        raise ValueError("empty")

    return 2


def _isiterable(x):
    # consider strings non-iterable for shape validation purposes,
    # that way they are printed out whole when caught as nonnumeric
    if isinstance(x, str):
        return False

    # collections.abc docs: "The only reliable way to determine
    # whether an object is iterable is to call iter(obj)."
    try:
        iter(x)
    except TypeError:
        return False

    return True


def float_list_to_csv_string(float_list):
    # Note: as in the Boon Nano SDK, there is no check that data dimensions
    # align with number of features and streaming window size.
    ndim = validate_dims(float_list)

    if ndim == 0:
        data_flat = [float_list]
    elif ndim == 1:
        data_flat = list(float_list)
    elif ndim == 2:
        data_flat = list(itertools.chain.from_iterable(float_list))
    else:
        raise ValueError("float_list is not in known format")

    for d in data_flat:
        if not isinstance(d, Number) or np.isnan(d):
            raise ValueError("contained {} which is not numeric".format(d.__repr__()))
    return ",".join([str(float(d)) for d in data_flat])


def packed_floats(data):
    """Validate data and convert to a packed float buffer"""

    if isinstance(data, str):
        data = data.split(",")

    data = np.array(data, dtype="float32")
    data = data.flatten()
    data = data.tobytes()

    return data


# def create_packed_float_file(input, output):
#    list_data = []
#    with open(input, 'r') as f:
#        csv_reader = csv.reader(f, delimiter=',')
#        for row in csv_reader:
#            for d in row:
#                list_data.append(float(d))
#
#    packed_floats = packed_floats(list_data)
#
#    with open(output, "wb") as f:
#        f.write(packed_floats)
#    print("wrote {} bytes to {}".format(len(packed_floats), output))
#
