# API methods.
You may get all methods by opening `/` page. Any method return response in API response format documented inside [/docs/API_RESPONSE.md](/docs/API_RESPONSE.md)

## Methods.
- `/user`
- - Returns user information by JWT token.
- - Params:
- - `token` = JWT token (Or from `Authorization` header).
- `/signup`
- - Creates new user and returns JWT token.
- - `username` = Your username.
- - `email` = Your email.
- - `password` = Your password.
- `/signin`
- - Login user and returns JWT token.
- - Params:
- - `login` = Your email or username.
- - `password` = Your password.
- `/changelog`
- - Returns changelog for the API.
