import dataclasses
import datetime
import json

import iso8601


@dataclasses.dataclass
class Result:
    # True if the update completed successfully.
    success: bool
    # The error message for update failure (empty string on success).
    error: str
    # Timestamp when the update process completes.
    timestamp: datetime.datetime
    # The version of code in the TinyPilot directory at the end of the update
    # process.
    version_at_end: str


def read(result_file):
    """Reads an update result file.

    Parses the contents of a result file into a Result object. The file should
    have a format like:

      {
        "success": true,
        "error": "",
        "timestamp": "2021-02-10T085735Z",
        "versionAtEnd": "1.4.2"
      }

    Args:
        result_file: A file containing JSON-formatted results of an update job.

    Returns:
        A Result object parsed from the file.
    """
    raw_result = json.load(result_file, cls=_ResultDecoder)
    return Result(success=raw_result.get('success', False),
                  error=raw_result.get('error', ''),
                  timestamp=raw_result.get(
                      'timestamp', datetime.datetime.utcfromtimestamp(0)),
                  version_at_end=raw_result.get('versionAtEnd', ''))


def write(result, result_file):
    """Serializes a Result object to a file as JSON.

    Args:
        result: A Result object containing results of an update job.
        result_file: File handle to which to serialize the result object.
    """
    # Convert snake_case members of dictionary to camelCase, as is convention
    # in JSON.
    result_dict = dataclasses.asdict(result)
    result_dict['versionAtEnd'] = result_dict['version_at_end']
    del result_dict['version_at_end']

    json.dump(result_dict, result_file, cls=_ResultEncoder)


class _ResultEncoder(json.JSONEncoder):

    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return iso8601.to_string(obj)
        return obj


class _ResultDecoder(json.JSONDecoder):

    def __init__(self, *args, **kwargs):
        json.JSONDecoder.__init__(self,
                                  object_hook=self._decode_object,
                                  *args,
                                  **kwargs)

    # pylint: disable=no-self-use
    def _decode_object(self, obj):
        if 'timestamp' in obj:
            obj['timestamp'] = iso8601.parse(obj['timestamp'])
        return obj
