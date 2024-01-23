# CS50-Finance

![Screenshot 2023-11-29 at 10 34 44](https://github.com/irfanali1995/IrfanAli-CodingProjects/assets/75564524/ba8bf19c-1406-4d2a-b6fd-f5b2d0c82adf)

**Description:** Stock web-app where user can register and lookup realtime stock by using Yahoo finance API, where they can purchase stock with pretend money .   

# Technologies Used:
 Flask, SQLite 3,HTML/CSS, Password Hashing, Stock Price Lookup (APIs), User Authentication, Forms and Input Handling, Session Management

For this project, I implemented the following functionality:

1. `register`: Allows a user to "register" on the site. The username and password are submitted via Flask and stored in a sqlite 3 database
2. `quote`: Allows a user to look up the price of a stock using the symbol
3. `buy`: Allows a user to buy the imaginary stock; Purchased stocks are saved to the database and money balance is updated
4. `index`: Displays an HTML summary table of the user's current funds and stocks
5. `sell`: Allows a user to sell stocks; Sold stocks are removed from the database and the money balance is updated
6. `change_password`: Allow user to change password
7. `add_money`: Allow user to add money with pretend card 

**NOTE**: All copy rights for this projects are here [here](https://cs50.harvard.edu/x/2020/tracks/web/finance/).   
