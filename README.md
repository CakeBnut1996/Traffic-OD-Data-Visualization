Origin-Destination Matrix Descriptive Data Analysis

- Number of OD pairs (OD Analysis.py)
- Missing Rate (OD Analysis.py)
- Temporal Patterns (OD Analysis.py)
- Spatial Patterns (Spatial_Analysis.py)

1. Number of OD pairs

<img width="529" alt="image" src="https://user-images.githubusercontent.com/46463367/167270115-20ef901b-0648-4c61-8067-f49173fa0f2d.png">

2. Missing Rate

Important links OD missing rate
Important links: hourly average traffic > 5. 
- It takes up 0.7% of total number of pairs
- Average missing rate from 8AM-5PM is 30%.

![image](https://user-images.githubusercontent.com/46463367/167270245-b829e231-6d37-4412-9d98-4d5ce51aa5ff.png)

Next, visualize OD with missing rate greater than 0.6 on the map (Width of the lines represents missing rate)
Conclusion: Longer OD tends to have more missing values.

<img width="227" alt="image" src="https://user-images.githubusercontent.com/46463367/167270263-ea58a398-36a4-4a4d-a953-a21f92d3f493.png">


3. School Season Departure Time Distribution 

![image](https://user-images.githubusercontent.com/46463367/167270131-6439d627-8c69-4ee3-90e4-22c802241734.png)


4. Spatial Pattern During School Season
Destination zones peak-hour volume in school season:

<img width="499" alt="image" src="https://user-images.githubusercontent.com/46463367/167270294-8d6bce2d-9fd0-4789-9f4a-55fbb0d68fa1.png">

Peak-hour and Off-peak Volume Comparison: 

<img width="485" alt="image" src="https://user-images.githubusercontent.com/46463367/167270321-acbbf7e7-bea0-4470-8ccb-31714e1d7b9e.png">

Notes: Some zones do not generate or attract trips at all during some time slots (green zones). There are more zero-traffic zones during off-peak hours.

Missing Values Distribution:
- Missing values: The zones with missing OD value includes north, southeast and southwest mountain area, thus counted as missing data.
- Conclusion: STL OD data represent the true values and can be used as input of DynusT.

<img width="317" alt="image" src="https://user-images.githubusercontent.com/46463367/167270342-26a80555-643c-40ad-b6a3-267173cef40c.png">

