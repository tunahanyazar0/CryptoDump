# CryptoDump
It is mainly a crypto app with multiple functions. Fırstly, it can guess crypto's price in the next year.  For that function I've used fbprophet module from facebook and some other modules.What fbprophet does is that FBProphet uses time as a regressor and tries to fit several linear and nonlinear function of time as components. By default, FBProphet will fit the data using a linear model but it can be changed to the nonlinear model (logistics growth) from its arguments. I have used the work of Benedict Neo (https://medium.com/bitgrit-data-science-publication/ethereum-price-prediction-with-python-3b3805e6e512) for the prophecy part in my project. It gives us the prices for the next year of the variety of cryptocurrencies by looking at the data of the prices form the previous years.For the identify the day that user at, I have used datetime module and to format this I've used stfrtime method. Secondly, it shows some news from the day you live in about crypto, stocks and some other things related to business. I made this part because news are influencing the price of stocks and due to that I wanted to let my user know the latest news. For that I've used news api (https://newsapi.org/) and python request module with its get method. News API is a simple JSON-based REST API for searching and retrieving news articles from all over the web. Using this, one can fetch the top stories running on a news website or can search top news on a specific topic (or keyword). Thirdly, I created a part in which you can see the opening price, closing price, highest price, lowest price and volume of the stock at the day the user at currently.To do that I have used yahoofinance (https://www.yahoofinanceapi.com/) api which get these informations in the time interval you have given. I have gived 1 day to see the latest values that comes from yesterday. What does yahoofinance do is that Finance is a media property that is part of the Yahoo! network. It provides financial news, data and commentary including stock quotes, press releases, financial reports, and original content. It also offers some online tools for personal finance management. Furthermore, my project can manage your portfolio with buying and selling fucntion which I mostly copied them from CS50 Finance. To get the stocks current prices, I've used the same api that has been used in the cs50 finance lecture because it is useful. And then I added a about part in which I added my informations. Lastly, there is a footer in which you can reach my personal accounts and send email by clicking to send mail part. For the styling, I have mainly used boostrap. I've used tables, input groups, footbars, colored table rows and table cells. For the layout, I have used some part of the cs50 especially for the buy, sell and portfolio part because It would be the time waste for me to create new one even though there is already one.
