import json
import traceback
import botocore.credentials
import jsonschema
import botocore

from tornado import web
from jupyter_server.base.handlers import JupyterHandler
from jsonschema.exceptions import ValidationError
from sagemaker_jupyterlab_emr_extension._version import __version__ as ext_version

from sagemaker_jupyterlab_extension_common.logging.logging_utils import HandlerLogMixin

from sagemaker_jupyterlab_emr_extension.schema.emr_serverless_api_schema import (
    list_serverless_applications_request_schema,
    get_serverless_application_request_schema,
)
from sagemaker_jupyterlab_emr_extension.converter.emr_serverless_converters import (
    convert_list_serverless_applications_response,
    convert_get_serverless_application_response,
)
from sagemaker_jupyterlab_emr_extension.utils.logging_utils import (
    EmrErrorHandler,
)

from sagemaker_jupyterlab_emr_extension.client.emr_serverless_client import (
    get_emr_serverless_client,
)

EXTENSION_NAME = "sagemaker_jupyterlab_emr_extension"
EXTENSION_VERSION = ext_version


class ListServerlessApplicationsHandler(HandlerLogMixin, JupyterHandler):
    # Do not rename or change the variable names, these are used by
    # loggers in common package.
    jl_extension_name = EXTENSION_NAME
    jl_extension_version = EXTENSION_VERSION

    """
    Response schema
    {
        applications: [ApplicationSummary]!
        errorMessage: String
    }
    """

    @web.authenticated
    async def post(self):
        self.set_header("Content-Type", "application/json")
        try:
            body = self.get_json_body()
            jsonschema.validate(body, list_serverless_applications_request_schema)
            self.log.info(
                f"List applications request {body}",
                extra={"Component": "ListServerlessApplications"},
            )
            roleArn = body.pop("roleArn", None)
            response = await get_emr_serverless_client(
                roleArn=roleArn
            ).list_applications(**body)
            converted_resp = convert_list_serverless_applications_response(response)
            self.set_status(200)
            self.finish(json.dumps(converted_resp))
        except web.HTTPError as e:
            message = e.log_message
            self.log.error(message)
            self.set_status(e.status_code)
            if e.status_code == 400:
                reply = dict(message="Invalid JSON in request", reason=e.reason)
                self.finish(json.dumps(reply))
            else:
                reply = dict(message=message, reason=e.reason)
                self.finish(json.dumps(reply))
        except (
            botocore.exceptions.ParamValidationError,
            jsonschema.exceptions.ValidationError,
        ) as error:
            self.log.error(
                "Invalid request {} {}".format(body, traceback.format_exc()),
                extra={"Component": "ListServerlessApplications"},
            )
            self.set_status(400)
            self.finish(
                json.dumps({"ErrorMessage": "Invalid request missing or wrong input"})
            )
        except botocore.exceptions.ConnectTimeoutError as error:
            helpful_context = (
                "Connection timed out. Looks like you do not have required networking setup to connect "
                "with EMR Serverless."
            )
            self.log.error(
                "SdkConnectError {}".format(traceback.format_exc()),
                extra={"Component": "ListServerlessApplications"},
            )
            self.set_status(400)
            error_message = {
                "code": "ConnectTimeoutError",
                "errorMessage": f"{helpful_context} Error message: {str(error)}",
            }
            self.finish(json.dumps(error_message))
        except botocore.exceptions.ClientError as error:
            self.log.error(
                "SdkClientError {}".format(traceback.format_exc()),
                extra={"Component": "ListServerlessApplications"},
            )
            msg = EmrErrorHandler.get_boto_error(error)
            self.set_status(msg.get("http_code"))
            self.finish(json.dumps(msg.get("message")))
        except Exception as error:
            self.log.error(
                "Internal Service Error: {}".format(traceback.format_exc()),
                extra={"Component": "ListServerlessApplications"},
            )
            self.set_status(500)
            self.finish(json.dumps({"error": str(error)}))


class GetServerlessApplicationHandler(HandlerLogMixin, JupyterHandler):
    # Do not rename or change the variable names, these are used by
    # loggers in common package.
    jl_extension_name = EXTENSION_NAME
    jl_extension_version = EXTENSION_VERSION

    """
    Response schema
    {
        application: Application
        errorMessage: String
    }
    """

    @web.authenticated
    async def post(self):
        self.set_header("Content-Type", "application/json")
        try:
            body = self.get_json_body()
            jsonschema.validate(body, get_serverless_application_request_schema)
            application_id = body["applicationId"]
            role_arn = body.pop("RoleArn", None)
            self.log.info(
                f"Get serverless application request {application_id}",
                extra={"Component": "GetServerlessApplication"},
            )
            response = await get_emr_serverless_client(
                roleArn=role_arn
            ).get_application(**body)
            self.log.info(
                f"Successfully got application for id {application_id}",
                extra={"Component": "GetServerlessApplication"},
            )
            converted_resp = convert_get_serverless_application_response(response)
            self.set_status(200)
            self.finish(json.dumps(converted_resp))
        except web.HTTPError as e:
            message = e.log_message
            self.log.error(message)
            self.set_status(e.status_code)
            if e.status_code == 400:
                reply = dict(message="Invalid JSON in request", reason=e.reason)
                self.finish(json.dumps(reply))
            else:
                reply = dict(message=message, reason=e.reason)
                self.finish(json.dumps(reply))
        except (
            botocore.exceptions.ParamValidationError,
            ValidationError,
        ) as error:
            self.log.error(
                "Invalid request {} {}".format(body, traceback.format_exc()),
                extra={"Component": "GetServerlessApplication"},
            )
            self.set_status(400)
            self.finish(
                json.dumps({"errorMessage": "Invalid request missing or wrong input"})
            )
        except botocore.exceptions.ClientError as error:
            self.log.error(
                "SdkClientError {}".format(traceback.format_exc()),
                extra={"Component": "GetServerlessApplication"},
            )
            msg = EmrErrorHandler.get_boto_error(error)
            self.set_status(msg.get("http_code"))
            self.finish(json.dumps(msg.get("message")))
        except Exception as error:
            self.log.error(
                "Internal Service Error: {}".format(traceback.format_exc()),
                extra={"Component": "GetServerlessApplication"},
            )
            self.set_status(500)
            self.finish(json.dumps({"errorMessage": str(error)}))
