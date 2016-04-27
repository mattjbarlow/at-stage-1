import logging
import boto3
import utils
from datetime import datetime
from dateutil.parser import parse
from utils import HTTPError
from boto3.dynamodb.conditions import Key, Attr


LOG = logging.getLogger()
logging.basicConfig()
LOG.setLevel(logging.INFO)

def get_operation_handler(operation):
    operation_handler_map = {
        'list_jobs': AtJob,
        'create_job': AtJob,
        'describe_job': AtJob,
        'delete_job': AtJob
    }
    return operation_handler_map[operation]

def lambda_handler(event, context):
    LOG.info("event is {}".format(event))
    try:
        operation = event['parameters']['gateway']['operationId']
        handler = get_operation_handler(operation)(
            event=event,
            context=context
        )
        LOG.info("Received operation {}".format(operation))
        return getattr(handler, operation)()
    except:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        traceback.print_exception(exc_type, exc_value, exc_traceback)
        msg = 'Got {0} error: {1}'.format(exc_type, exc_value)
        raise HTTPError(status=500, message=msg)

class AtJob:
    def __init__(self, event=None, context=None):
        stage_variables = event['parameters']['gateway']['stage-variables']
        self.db_table = stage_variables.get('DBTable')
        self.dynamo_connector = boto3.resource('dynamodb')
        self.event = event
        self.context = context
        self.query_params = event['parameters']['request']['query-params']
        self.path_params = event['parameters']['request']['path-params']
        self.body = event['parameters']['request']['body']

    def list_jobs(self):
        return

    def create_job(self):
        table = self.dynamo_connector.Table(self.db_table)
        try:
            lambdaArn = self.body['lambdaArn']
            time = self.body['time']
        except KeyError as exc:
            raise HTTPError(status=400,
                            message='Missing required body fields: %s' % exc)

        try:
            parse(time)
        except ValueError as exc:
            raise HTTPError(status=400,
                            message='Invalid date format: %s' % exc)

        db_item = {
            'jobid': utils.random_id(),
            'lambdaArn': lambdaArn,
            'time': time,
            'created_at': str(datetime.now()),
            'modified_at': str(datetime.now())
        }

        try:
            table.put_item(
                Item=db_item
            )

        except Exception as exc:
            warning_string = "Error creating new At Job DB entry {}"
            LOG.warning(warning_string.format(lambdaArn), exc_info=exc)
            raise

        return db_item

    def describe_job(self):
        return

    def delete_job(self):
        return
