# virtual_stock_trading

![Screenshot 2024-01-23 at 01 23 02](https://github.com/irfanali1995/virtual_stock_trading/assets/75564524/8ce4c64f-58cb-47f8-a54e-61440ebcc4dc)

**Description:** Stock web-app where user can register and lookup realtime stock by using Yahoo finance API, where they can purchase stock with pretend money .   

# Technologies Used:
 - Flask
 - SQLite 3
 - HTML/CSS
 - yFinance API
 - Password hashing with Werkzeug


For this project, I implemented the following functionality:

1. `register`: Allows a user to "register" on the site. The username and password are submitted via Flask and stored in a sqlite 3 database
2. `quote`: Allows a user to look up the price of a stock using the symbol
3. `buy`: Allows a user to buy the imaginary stock; Purchased stocks are saved to the database and money balance is updated
4. `index`: Displays an HTML summary table of the user's current funds and stocks
5. `sell`: Allows a user to sell stocks; Sold stocks are removed from the database and the money balance is updated
6. `change_password`: Allow user to change password
7. `add_money`: Allow user to add money with pretend card 

**NOTE**: All copy rights for this projects are here [here](https://cs50.harvard.edu/x/2020/tracks/web/finance/).   

