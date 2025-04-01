import base64
import json
import os
import time
from functools import wraps

import numpy as np
import urllib3

from .api.default_api import DefaultApi
from .api_client import ApiClient
from .configuration import Configuration
from .models import *
from .rest import ApiException as e


class ApiException(e):
    pass


class AmberV2Client:
    """Main client which interfaces with an amber server. Amber account
    credentials are specified through discovered within a .Amber.license file located in the
    home directory, or optionally overridden using environment variables.

    Args:
        kwargs:
          Direct specification:
            server: full URL for amber server
            oauth_server: full URL for oauth server
            license_key: Amber license_key
            secret_key: Amber secret key
            timeout: Timeout value for all requests

          License File:
              license_file: path to license file (defaults to ~/.Amber.license) (AMBER_LICENSE_FILE)
              profile_name: profile name withing .Amber.license (defaults to "default") (AMBER_PROFILE_NAME aka AMBER_LICENSE_ID)

          Profile Dictionary:
              profile: profile dictionary

    Environment variables:
        `AMBER_LICENSE_KEY`: license key

        `AMBER_SECRET_KEY`: secret key

        `AMBER_SERVER`: amber server address

        `AMBER_OAUTH_SERVER`: amber oauth server address, defaults to AMBER_SERVER if unset

        `AMBER_SSL_CERT`: path to ssl client cert file (.pem)

        `AMBER_SSL_VERIFY`: Either a boolean, in which case it controls whether we verify the server’s TLS certificate, or a string, in which case it must be a path to a CA bundle to use

        `AMBER_LICENSE_FILE`: file containing amber credentials

        `AMBER_PROFILE_NAME`: named entry within the AMBER_LICENSE_FILE

        `AMBER_LICENSE_ID`: alias for AMBER_PROFILE_NAME
    """

    def __init__(self, **kwargs):

        self.license_file = "~/.Amber.license"
        self.profile_name = "default"
        self.profile = None
        self.server = None
        self.oauth_server = None
        self.license_key = None
        self.secret_key = None
        self.verify_ssl = ""
        self.timeout = None

        # load all kwargs
        self.__dict__.update(kwargs)

        # load from license file
        file_profile = self._from_license_file(self.profile_name, self.license_file)
        if file_profile:
            self.__dict__.update(file_profile)

        # load from specified profile
        if self.profile:
            self.__dict__.update(self.profile)

        # environment variables override kwargs
        env_profile = self._from_env()
        self.__dict__.update(env_profile)

        # check for required settings
        if not self.server:
            raise ApiException("No server specified")
        if not self.secret_key:
            raise ApiException("No secret key specified")
        if not self.license_key:
            raise ApiException("No license key specified")
        # oauth_server should be server if not specified
        if not self.oauth_server:
            self.oauth_server = self.server

        # Server type identification.  "basic" or "aws"
        self.server_type = None

        # generate separate configurations for talking to the authentication server and core amber api
        self.api_config = Configuration()
        self.api_config.host = self.server
        self.oauth_config = Configuration()
        self.oauth_config.host = self.oauth_server

        if self.verify_ssl != "":
            self.api_config.verify_ssl = self.oauth_config.verify_ssl = self.verify_ssl.lower() in ["true", "1", "t"]
            urllib3.disable_warnings()

        if self.timeout is not None:
            self.api_config.request_timeout = self.oauth_config.timeout = self.timeout

        # init oauth2 tokens
        self.access_token = ""
        self.refresh_token = ""
        self.reauth_time = 0

        self.api = DefaultApi(ApiClient(self.api_config))
        self.oauth_api = DefaultApi(ApiClient(self.oauth_config))

    def _from_license_file(self, profile_name: str = "default", license_file: str = "~/.Amber.license"):
        """
        Args:
            profile_name: (type: str) profile name from .Amber.license file
            license_file: (type: str) path to .Amber.license file
        """
        filepath = os.environ.get("AMBER_LICENSE_FILE", license_file)
        profile_name = os.environ.get("AMBER_PROFILE_NAME", os.environ.get("AMBER_LICENSE_ID", profile_name))
        file_data = {}

        if filepath is not None:
            filepath = os.path.expanduser(filepath)
            if os.path.exists(filepath):
                try:
                    with open(filepath, "r") as f:
                        file_data = json.load(f)
                except json.JSONDecodeError as e:
                    raise ApiException(status=406, reason="JSON formatting error in license file: {}, line: {}, col: {}".format(e.msg, e.lineno, e.colno))
            else:
                # it's fine to not have a .Amber.license file
                return {}

        if file_data is None:
            return {}

        profile = file_data.get(profile_name, None)
        if profile is None:
            raise ApiException(status=406, reason=f"profile {profile_name} not found")

        # when specified in license file, oauth-server appears with a hyphen, convert to underscore
        if "oauth-server" in profile:
            profile["oauth_server"] = profile["oauth-server"]
            del profile["oauth-server"]
        if "license-key" in profile:
            profile["license_key"] = profile["license-key"]
            del profile["license-key"]
        if "secret-key" in profile:
            profile["secret_key"] = profile["secret-key"]
            del profile["secret-key"]

        return profile

    def _from_env(self):
        """

        Environment:
            `AMBER_LICENSE_KEY`: license key

            `AMBER_SECRET_KEY`: secrect key

            `AMBER_SERVER`: amber server address

            `AMBER_OAUTH_SERVER`: amber oauth server address

            `AMBER_SSL_CERT`: path to ssl client cert file (.pem)

            `AMBER_SSL_VERIFY`: Either a boolean, in which case it controls whether we verify the server’s TLS certificate, or a string, in which case it must be a path to a CA bundle to use

        Raises:
            ApiException: if error supplying authentication credentials
        """
        profile = {}
        license_key = os.environ.get("AMBER_LICENSE_KEY", None)
        if license_key is not None:
            profile["license_key"] = license_key
        secret_key = os.environ.get("AMBER_SECRET_KEY", None)
        if secret_key is not None:
            profile["secret_key"] = secret_key
        server = os.environ.get("AMBER_SERVER", None)
        if server is not None:
            profile["server"] = server
        oauth_server = os.environ.get("AMBER_OAUTH_SERVER", None)
        if oauth_server is not None:
            profile["oauth_server"] = oauth_server
        ssl_cert = os.environ.get("AMBER_SSL_CERT", None)
        if ssl_cert is not None:
            profile["ssl_cert"] = ssl_cert
        ssl_verify = os.environ.get("AMBER_SSL_VERIFY", None)
        if ssl_verify is not None:
            profile["ssl_verify"] = ssl_verify

        return profile

    def __authenticate(f):
        @wraps(f)
        def inner(self, *args, **kwargs):
            if time.time() <= self.reauth_time:
                return f(self, *args, **kwargs)

            try:
                if self.access_token == "":
                    # initial authentication, use license and secret key
                    body = PostOauth2AccessRequest(self.license_key, self.secret_key)
                    response = self.oauth_api.post_oauth2_access_with_http_info(body)
                    self.access_token = response[0].id_token
                    self.refresh_token = response[0].refresh_token
                    self.expires_in = int(response[0].expires_in)
                    self.secret_key = ""  # clear the secret_key from plain site
                    if self.server_type is None:
                        # set server type if not discovered
                        if response[2].get("x-amz-apigw-id") is not None:
                            self.server_type = "aws"
                        else:
                            self.server_type = "basic"
                else:
                    # we have authenticated once, use the refresh token
                    body = PostOauth2RefreshRequest(self.refresh_token)
                    response = self.oauth_api.post_oauth2_refresh(body)
                    self.access_token = response.id_token
                    self.refresh_token = response.refresh_token
                    self.expires_in = int(response.expires_in)

            except Exception as e:
                raise ApiException(status=401, reason="Authentication failed: invalid credentials")

            self.api_config.api_key["Authorization"] = self.access_token
            self.api_config.api_key_prefix["Authorization"] = "Bearer"
            self.reauth_time = time.time() + self.expires_in - 60

            return f(self, *args, **kwargs)

        return inner

    @__authenticate
    def get_version(self) -> GetVersionResponse:
        """

        Return version information for the API.

        Returns:
            `boonamber.v2.models.get_version_response.GetVersionResponse`

        Example:
            ```
            amber = AmberClientV2()
            version = amber.get_version()
            print(version.to_dict())
            ```

        """
        return self.api.get_version(_request_timeout=self.timeout)

    @__authenticate
    def delete_model(self, model_id: str):
        """

        Permanently delete the specified model.

        Args:
            model_id: (type: str) (required)

        """
        self.api.delete_model(model_id=model_id)

    @__authenticate
    def get_root_cause(self, model_id: str, **kwargs) -> GetRootCauseResponse:
        """

        Return a measure of the significance of each feature in the creation of a cluster. The values range from 0 to 1 where a relatively high value represents a feature that was influential in creating the new cluster. No conclusions can be drawn from values close to zero. This measure can be computed for existing clusters or for individual vectors directly.

        Args:
            model_id: (type: str) (required)
            clusters: (type: str or array-like) Clusters to analyze (list of comma-separated integers).
            vectors: (type: str or array-like) Vectors to analyze, as a flat list of comma-separated floats. Number of values must be a multiple of the configured number of features.

        Returns:
            `boonamber.v2.models.get_root_cause_response.GetRootCauseResponse`

        """
        import numpy as np

        # vectors
        if "vectors" in kwargs.keys():
            if isinstance(kwargs["vectors"], (list, np.ndarray, tuple)):
                dimensions = len(np.asarray(kwargs["vectors"]).shape)
                # 1 vector given
                if dimensions == 1:
                    kwargs["vectors"] = ",".join([str(v) for v in kwargs["vectors"]])
                # 2d array of vectors
                elif dimensions == 2:
                    kwargs["vectors"] = [",".join([str(v) for v in row]) for row in kwargs["vectors"]]
                    kwargs["vectors"] = "],[".join(kwargs["vectors"])
                else:
                    raise ApiException(status=406, reason="invalid dimensions of vectors given: should be 1 or 2D but got {}D".format(len(np.asarray(kwargs["vectors"]).shape)))
                kwargs["vectors"] = "[[{}]]".format(kwargs["vectors"])
            # not a string or not formatted as a string list
            elif not isinstance(kwargs["vectors"], str):
                raise ApiException(status=406, reason="invalid formatting of vectors. Expecting a array-type or numbers or string")
        # clusters
        if "clusters" in kwargs.keys():
            if isinstance(kwargs["clusters"], (list, np.ndarray, tuple, str, int, float)):
                dimensions = len(np.asarray(kwargs["clusters"]).shape)
                # 1 value
                if dimensions == 0:
                    kwargs["clusters"] = f"[{kwargs['clusters']}]"
                # list of clusters
                elif dimensions == 1:
                    kwargs["clusters"] = "[{}]".format(",".join([str(c) for c in kwargs["clusters"]]))
                else:
                    raise ApiException(status=406, reason="invalid dimensions of clusters given: should be 0 or 1D but got {}D".format(len(np.asarray(kwargs["clusters"]).shape)))
            else:
                raise ApiException(status=406, reason="invalid formatting of clusters. Expecting a array-type or numbers or string")

        if "clusters" in kwargs.keys():
            return self.api.get_model_root_cause(model_id=model_id, clusters=kwargs["clusters"])
        if "vectors" in kwargs.keys():
            return self.api.get_model_root_cause(model_id=model_id, vectors=kwargs["vectors"])

    @__authenticate
    def get_config(self, model_id: str) -> PostConfigResponse:
        """

        Get the configuration of the specified model.

        Args:
            model_id: (type: str) (required)

        Returns:
            `boonamber.v2.models.post_config_response.PostConfigResponse`

        """
        return self.api.get_model_config(model_id=model_id)

    @__authenticate
    def get_model(self, model_id: str) -> PostModelResponse:
        """

        Return metadata for the specified model.

        Args:
            model_id: (type: str) (required)

        Returns:
            `boonamber.v2.models.post_model_response.PostModelResponse`

        """
        return self.api.get_model(model_id=model_id)

    @__authenticate
    def get_models(self) -> GetModelsResponse:
        """

        Return `id` and `label` for all models belonging to the user.

        Returns:
            `boonamber.v2.models.get_models_response.GetModelsResponse`

        """
        return self.api.get_models()

    @__authenticate
    def get_pretrain(self, model_id: str) -> GetPretrainResponse:
        """

        Get the pretraining status of the specified model.

        Args:
            model_id: (type: str) (required)

        Returns:
            `boonamber.v2.models.get_pretrain_response.GetPretrainResponse`

        """
        return self.api.get_model_pretrain(model_id=model_id)

    @__authenticate
    def get_status(self, model_id: str) -> GetStatusResponse:
        """

        Get the current state and learning progress of the specified model.

        Args:
            model_id: (type: str) (required)

        Returns:
            `boonamber.v2.models.get_status_response.GetStatusResponse`

        """
        return self.api.get_model_status(model_id=model_id)

    @__authenticate
    def get_nano_status(self, model_id: str) -> GetNanoStatusResponse:
        """

        Get the current nano status of the specified model.

        Args:
            model_id: (type: str) (required)

        Returns:
            `boonamber.v2.models.get_nano_status_response.GetNanoStatusResponse`

        """
        return self.api.get_model_nano_status(model_id=model_id)

    @__authenticate
    def get_diagnostic(self, model_id: str, dir: str) -> str:
        """

        Get the current summation of the specified model

        Args:
            model_id: (type: str) (required)
            dir: (type: str) (required) path to save the diagnostic tar file

        Returns:
            str

        """
        if not os.path.exists(dir):
            raise ApiException(status=406, reason="target directory does not exist")
        dir = os.path.expanduser(dir)
        path = f"{dir}/{model_id}-diagnostic.tar"

        results = self.api.get_model_diagnostic(model_id=model_id)

        with open(path, "wb") as fp:
            fp.write(results)
        return path

    @__authenticate
    def post_config(self, model_id: str, body: PostConfigRequest) -> PostConfigResponse:
        """

        Configure the specified model. Wipes all progress and puts the model in the `Buffering` state.

        Args:
            model_id: (type: str) (required)
            body: (type: `boonamber.v2.models.post_config_request.PostConfigRequest`) configuration to apply

        Returns:
            `boonamber.v2.models.post_config_response.PostConfigResponse`

        """

        return self.api.post_model_config(model_id=model_id, body=body)

    @__authenticate
    def post_data(self, model_id: str, data, save_image: bool = True) -> PostDataResponse:
        """

        Send data to the specified model, and get back the resulting analytics and model status.

        Args:
            model_id: (type: str) (required)
            data: (type: str or array-like) (required) data vector or vectors as a flattened list of comma-separated values
            save_image: (type: boolean) whether or not to save the model (only applies to on prem)

        Returns:
            `boonamber.v2.models.post_data_response.PostDataResponse`

        """

        # accept data as a list
        if isinstance(data, (list, np.ndarray)):
            data = np.array(data, dtype=str).flatten()
            data = ",".join(data)
        elif not isinstance(data, str):
            raise ApiException(status=406, reason="invalid data: {}".format(type(data)))
        # post data
        body = PostDataRequest(data=data, save_image=save_image)
        return self.api.post_model_data(model_id=model_id, body=body)

    @__authenticate
    def post_model(self, metadata: PostModelRequest) -> PostModelResponse:
        """

        Create a new model and return its unique identifier.

        Args:
            metadata: (type: `boonamber.v2.models.post_model_request.PostModelRequest`) (required) initial metadata for new model

        Returns:
            `boonamber.v2.models.post_model_response.PostModelResponse`

        """
        return self.api.post_model(body=metadata)

    @__authenticate
    def copy_model(self, model_id: str, label: str = None) -> PostModelResponse:
        """

        Copy a model and return the new model information.

        Args:
            model_id: (type: str) (required)
            label: (type: str) label for new model (uses previous label if unspecified)

        Returns:
            `boonamber.v2.models.post_model_response.PostModelResponse`

        """
        kwargs = {}
        if label:
            kwargs["body"] = PostModelCopyRequest(label=label)

        return self.api.post_model_copy(model_id, **kwargs)

    @__authenticate
    def post_outage(self, model_id: str):
        """

        Resets the streaming window generated by `streamingWindow`. This endpoint should be called after a data outage before resuming streaming.

        Args:
            model_id: (type: str) (required)

        """
        self.api.post_model_outage(model_id=model_id)

    @__authenticate
    def migrate_model(self, v1_model_id: str):
        """migrate a v1 sensor to a v2 model


        Args:
            v1_model_id: (type: str) version 1 sensor id (required)

        Returns:
            `boonamber.v2.models.post_model_response.PostModelResponse`

        """

        return self.api.post_model_migrate(v1_model_id=v1_model_id)

    @__authenticate
    def post_pretrain(self, model_id: str, data, chunk_size: int = 400000, block: bool = True, **kwargs) -> PostPretrainResponse:
        """pretrain model with an existing dataset

        Args:
            model_id: (type: str) (required)
            data: (type: str or array like) data to process
            chunk_size: (type: int) number of portions to send the data over
            block: (type: boolean) wait until pretraining finishes before returning

        Returns:
            `boonamber.v2.models.post_pretrain_response.PostPretrainResponse`

        """
        # Server expects data as a plaintext string of comma-separated values.
        try:
            if isinstance(data, str):
                data = data.split(",")

            data = np.array(data, dtype="float32")
            data = data.flatten()
            data = data.tobytes()
        except ValueError as e:
            raise ApiException(status=406, reason="invalid data: {}".format(e))

        # headers = {"content-type": "application/octet-stream"
        param = PostPretrainRequest(data="", format="packed-float")

        # compute number of chunks to send
        num_chunks = int(len(data) / chunk_size)
        if len(data) % chunk_size != 0:
            num_chunks += 1

        txn_id = ""
        for chunk_num in range(0, num_chunks):
            # create chunk specifier, .ie 1:3, 2:3, 3:3
            chunkspec = "{}:{}".format(chunk_num + 1, num_chunks)

            # construct next chunk
            start = chunk_num * chunk_size
            end = start + chunk_size
            if end > len(data):
                end = len(data)
            param.data = base64.b64encode(data[start:end]).decode("ascii")

            response = self.api.post_model_pretrain(
                model_id=model_id,
                chunkspec=chunkspec,
                txn_id=txn_id,
                body=param,
            )
            txn_id = response.txn_id

        if not block:
            return response

        while response.status == "Pretraining":
            time.sleep(3)
            response = self.get_pretrain(model_id=model_id)

        return response

    @__authenticate
    def enable_learning(self, model_id: str, body: PostLearningRequest) -> PostLearningResponse:
        """

        Update model configuration and re-enable learning

        Args:
            model_id: (type: str) (required)
            body: (type: `boonamber.v2.models.PostLearningRequest`) updates to apply

        Returns:
            `boonamber.v2.models.PostLearningRequest`

        """
        return self.api.post_model_learning(model_id=model_id, body=body)

    @__authenticate
    def put_data(self, model_id: str, body: PutDataRequest) -> PutDataResponse:
        """update fusion vector and get back results

        Args:
            model_id: (type: str) (required)
            body: (type: `boonamber.v2.models.put_data_request.PutDataRequest`) (required) updates to the fusion vector

        Returns:
            `boonamber.v2.models.put_data_response.PutDataResponse`

        """
        return self.api.put_model_data(model_id=model_id, body=body)

    @__authenticate
    def update_label(self, model_id: str, label: str) -> PostModelResponse:
        """

        Update metadata for the specified model.

        Args:
            model_id: (type: str) (required)
            label: (type: str) (required) updates to apply

        Returns:
            `boonamber.v2.models.post_model_response.PostModelResponse`

        """
        metadata = PutModelRequest(label=label)
        return self.api.put_model(model_id=model_id, body=metadata)
