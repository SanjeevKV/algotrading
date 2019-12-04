# AlgoTrading
The main aim of the project is to get a continuous and reliable profit using algorithms for making trading decisions on BSE and NSE.

# Naming Convention
1. module_name 
2. package_name 
3. ClassName 
4. method_name 
5. ExceptionName 
6. function_name 
7. GLOBAL_CONSTANT_NAME 
8. global_var_name 
9. instance_var_name 
10. function_parameter_name 
11. local_var_name

# RoadMap
Step 1: Build modules to use kite APIs and make necessary actions possible  
Step 2: Use a simple testFile to test the functions in the modules  
Step 3: Implement a simple algorithm to make smart trading decisions  
Step 4: Test the effectiveness of the algorithm on sample data  
Step 5: Decide the machine on which the algorithm runs eternally  
Step 6: Get the API access from Zerodha and deploy the repository on the decided machine and monitor the live trading  

# Improvements
1. Algorithm used to make the decision can be improved
2. Hack-around the dependency on Zerodha
3. If the algorithms are successful, we can expose some functionalities as FaaS (Functionality as a Service)

# Algorithm 1 - StepDeals
Step 1: Identify N(potentially successful) companies to invest on  
Step 2: Divide the initial Principal(P) into N parts Pi  
Step 3: Let's say Invest-Reserve ratio is Ri
Step 4: Buy (Pi * Ri) worth of shares in the company 'i' for delivery with limit order at LTPi  
Step 5:  
Define Step % for every company Si
1. Increasing function LTPi
  1. A lot Lj is already bought at LTPi and a lot Lj-1 is already bought at LTPi - LTPi * Si / 100 : Sell the lots Lk where 0 < k < j
  2. A lot Lj-1 is bought at (L-1)TPi but not Lj at LTPi : Buy the lot Lj at (L-1)TPi + (L-1)TPi * Si / 100
2. Decreasing function LTPi
  1. A lot Lj is already bought at LTPi : Sell all the lots Lk where 0 < k < j
  2. A lot Lj is not already bought at LTPi : Buy a lot at LTPi