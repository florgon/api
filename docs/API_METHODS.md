# API methods.
You may get all methods by opening `/` page.

- /user
- - Returns user information by JWT token.
- - Params:
- - `token` = JWT token.
- /signup
- - Creates new user and returns JWT token.
- - `username` = Your username.
- - `email` = Your email.
- - `password` = Your password.
- /signin
- - Login user and returns JWT token.
- - Params:
- - `login` = Email or username.
- - `password` = Your password.