# Downlinking

### Introduction

We're interpreting a signal sent from one device to another in the form of changes in value to a timeseries trace. 

### Timeseries traces

Let’s generate some data first.

```
rpm = [0 for i in range(5000)]
df = pd.DataFrame()
df['rpm'] = rpm
df.loc[1000:1700] = 50
df.loc[2500:2800] = 50
df.loc[3000:4500] = 50
        
def generate_downlink(start, end, width, height, up):
    for i in range(start, end, width):
        if up:
            up = False
            df.loc[i:i+width] = height + 5
        else:
            up = True
            df.loc[i:i+width] = height - 5

generate_downlink(1100, 1490, 30, 50, up=True)
generate_downlink(2600, 2750, 30, 50, up=True)
generate_downlink(3100, 3430, 30, 50, up=True)
generate_downlink(3830, 4160, 30, 50, up=True)

generate_downlink(1190, 1250, 60, 50, up=False)
generate_downlink(1370, 1430, 60, 50, up=False)
generate_downlink(3920, 3980, 60, 50, up=False)
```

The dataframe we’re using has time in one-second increments as its index. Each signal value is recorded over a one-second interval.

This is a transactional dataframe, or a list of individual observations. Each row corresponds to one signal value. 

### Visualizing the trace

We can plot a column this way:

```
%matplotlib inline

plt.figure(figsize=(15,3))
plt.xlabel('Time in seconds')
plt.ylabel('Device RPM')
df['rpm'].plot()
```


### Building blocks

rolling()

groupby()

Allows us to perform aggregate functions on groups of rows separately instead of the entire dataframe. In this case we want the maximum rpm value per connection, not the maximum rpm value of the entire dataframe.

transform()

We first want to record when the signal value changes. 

```
df['rpm_changed'] = ((df['rpm'] != 0) & (df['rpm'].diff() > 0)).astype(int)
```

This boolean flag goes to 1 when the rpm value starts above 0 and quickly switches to a new value. 

Next we want to  count the number of times this kind of change happens. 

cumsum()

Keeps track of the running sum between rows. We’ll often use the cumsum() function to keep a running count of the number of times something has happened so far. 

```
df['change_num'] = df['rpm_changed'].cumsum().astype(int)
```

We’ll often use the cumsum() function to keep a running count of the number of times something has happened so far. 

Finally, we want to record the number of times the rpm has changed within a rolling window long enough to cover the downlink period.

```
df['change_counts_downlink_width'] = df['rpm_changed'].rolling((2*60), center=False).sum()
df['change_counts_downlink_width_reverse'] = df[::-1]['rpm_changed'].rolling((2*60), center=False).sum()[::-1]
```
The rolling window gives us a sum of the number of times the rpm has changed within the 120 second time period we’ve chosen to look at. We can use rolling windows to identify a sustained period of activity over a stretch of time. 

### Identify downlinks

```
df['downlink'] = ((df['change_counts_downlink_width'] > 0) & (df['change_counts_downlink_width_reverse'] > 0)).astype(int)
df['downlink_num'] = (df['downlink'].astype(int).diff() == 1).cumsum() 
```

The downlink flag tells us whether we are currently in a downlink or not. If both change counts are greater than 0, we are in a downlink. 

change counts



reverse change counts



downlink



change width



### Groupby/transform

```
df['high_point'] = df[df['downlink'] == 1].groupby('downlink_num').transform('max')['rpm']
df['low_point'] = df[df['downlink'] == 1].groupby('downlink_num').transform('min')['rpm']
```

We use groupby here to identify the high and low points per downlink number, and transform to write this back into the original dataframe.

Groupby allows us to perform aggregate functions on groups of rows separately instead of the entire dataframe. In this case we want the maximum rpm value per connection, not the maximum rpm value of the entire dataframe. 

