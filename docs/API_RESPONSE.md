# API response.
Any method return response in API response format documented inside here.


## Success.
When there is no errors and all OK, API returns JSON like that:
```
  "v": "*",
  "success": {
      *
  }
}
```
where `v` is API version, and `success` is container for data.

## Error.
When there is error(s), API returns JSON like that:
{
  "v": "*",
  "error": {
    "message": "*",
    "code": *,
    "status": *
  }
}
```
where `v` is API version, and `error` is container for error, where `message` is message for developer (you supposed to use error code for message user), `code` is the API error code, which is documented inside [/docs/API_ERROR_CODES.md](/docs/API_ERROR_CODES.md), and `status` is HTTP status code.