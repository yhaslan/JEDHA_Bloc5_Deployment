import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from PIL import Image

### Config
st.set_page_config(
    page_title="GetAround Analysis",
    page_icon= "🚗",
    layout="wide"
)


DATA_URL = ("https://jedha-getaround-project.s3.amazonaws.com/get_around_delay_analysis.xlsx")

st.title("GetAround Delay Analysis Web Dashboard🚗 ")

st.markdown("""
    Welcome to the Streamlit Dashboard of Getaround app! 👋
    Founded in 2009 with the goal to create a more affordable alternative to car-rental, 
    Getaround has rapidly increased its market share and 
    connected thousands of users in this car-sharing community.

    When renting a car, we ask our drivers to complete a checkin flow at pick-up and 
    a checkout flow at drop-off.

    The official purpose of this policy is :
    - to document pre-rental and post-rental damages
    - to compare fuel levels
    - to calculate the extra mileage
    in order to make sure that there are no additional costs to bear by our drivers.

    On the other hand, this dashboard is to explore a more interesting question and make a fun analysis on this data!
    By examining the data on check-in and check-out times for consecutive rental bookings, we will try to understand how
    often our drivers are late for checkout and to what extent this affect the next driver's cancelation decision!

    Finally, we will ask ourselves whether it would be more profitable for the business to deploy a minimum threshold
    for the time interval between two consecutive rentals. We will try to make two important decisions on:
      * threshold: how long should the minimum delay be?
    * scope: should we enable the feature for all cars? only Connect cars?


""")

@st.cache_data
def load_data():
    data = pd.read_excel(DATA_URL, sheet_name='rentals_data')
    
    data['previous_ended_rental_id'] = data['previous_ended_rental_id'].astype('Int64', errors = 'ignore').astype(str)
    data['rental_id'], data['car_id'] = data['rental_id'].astype(str), data['car_id'].astype(str)
    return data

st.subheader("Load and showcase data")

data_load_state = st.text('Loading data ...')
data = load_data()
data_load_state.text("")

if st.checkbox('Show raw data'):
    st.subheader('Raw data')
    st.write(data.head(100)) 


st.subheader("Let's find out what each variable means")
metadata = pd.read_excel(DATA_URL, sheet_name='Documentation')
pd.set_option('display.max_colwidth', None)
st.write(metadata)

st.header("Time to Explore")

st.subheader("Cancelation Rate")

# Create Seaborn histogram plot
df = data.groupby(['state'])['state'].count().reset_index(name='count')
fig = px.pie(df, values='count', names='state')
st.markdown("""
    It looks like the cancelation rate is around 15% in our dataset.
""")
            
st.subheader("Share of Consecutive Rentals")
st.markdown("""This graph shows the number and percentage of rentals which are followed
by another rental for the same vehicle within the next 12 hours after the anticipated checkout time. """)
data['second_rental'] = np.where(data['time_delta_with_previous_rental_in_minutes'].isna(), 0, 1)
df = data.groupby(['second_rental'])['second_rental'].count().reset_index(name='count')
fig = px.pie(df, values='count', names='second_rental')
st.plotly_chart(fig, height = 600, use_container_width=True)
st.markdown("""The share of the cars that have a second rental within the next 12 hours is 8.64% of our dataset,
 which corresponds to 1841 times.""")

st.subheader("Time Intervals and Delays")
col1, col2 = st.columns(2)
with col1:
    st.markdown("**Time Intervals between anticipated check-outs and next-check-in**")
    fig = px.histogram(data, x="time_delta_with_previous_rental_in_minutes")
    fig.update_layout(bargap=0.8)
    st.plotly_chart(fig,height = 400, use_container_width=True)
with col2:
    st.markdown("**Delays in minutes**")
    lower_bound = data['delay_at_checkout_in_minutes'].mean() - data['delay_at_checkout_in_minutes'].std()
    upper_bound = data['delay_at_checkout_in_minutes'].mean() + data['delay_at_checkout_in_minutes'].std()

    df = data[(data['delay_at_checkout_in_minutes'] > lower_bound) & (data['delay_at_checkout_in_minutes'] < upper_bound)]
    fig = px.histogram(df, x="delay_at_checkout_in_minutes")
    fig.update_layout(bargap=0.01)
    st.plotly_chart(fig, height = 400 , use_container_width=True)

st.markdown("""
- The figure on the left shows that out of 1841 cases where there was a second rental, near 400 was planned 
with nearly less than an hout time interval between the previous checkout and next check-in! 
This is nearly 25% of the cases!
- As we can see the majority of the observations are clustered within just one standard deviation from the mean delay time.
- It is quite rare to be late more than 5 hours.

""")



st.subheader("How often are drivers late for the next check-in?")
df2 = data[['rental_id', 'delay_at_checkout_in_minutes']]
df2 = df2.rename(columns={'rental_id': 'previous_ended_rental_id', 
                          'delay_at_checkout_in_minutes': 'previous_drivers_delay_in_mins'})
data = pd.merge(data, df2, on='previous_ended_rental_id', how='left')
data['minutes_passed_checkin_time'] = data['previous_drivers_delay_in_mins'] - data['time_delta_with_previous_rental_in_minutes']

def is_late(x):
    if x > 0:
        return "late"
    elif x < 0:
        return "not late"
    else:
        return np.nan
data['is_late_for_next_checkin'] = data['minutes_passed_checkin_time'].apply(is_late)
df = data[data['is_late_for_next_checkin'].isna()==False]
df = df.groupby(['is_late_for_next_checkin'])['is_late_for_next_checkin'].count().reset_index(name='count')
fig = px.pie(df, values='count', names='is_late_for_next_checkin')
st.plotly_chart(fig, height = 600, use_container_width=True)
st.markdown("""
Note that there is a tiny mismatch in the dataset. 
- We had 1841 observations that had a second rental in the next 12 hours.
- But the data on whether the vehicle was late for the next check-in contains a total of 1724 obsrvation, 
so some observations should be missing.
- Out of 1724 cases where we know if the previous driver passed the next check-in hour, the cars weer late for next
check-in 218 times, which makes near 12% of the cases of consecutive rentals.
""")
            
st.subheader('How does this impact the next driver?')
image = Image.open('swarmplot.png')
col1, col2, col3 = st.columns([1.5, 5, 1.5])
col2.image(image, caption='Cancelation by the delay time')
      
st.markdown("""
- In the most cases of consecutive rentals, vehicles were returned between 14 hours before to 
2 hours after original checkout date.
- The ratio of canceled:non-canceled bookings seems to have increased gradually if the car still had not returned 5 hours before the next check-in. This might be either due to company's notifying the next driver about the current situation and driver ending up finding other options and canceling immediately or due to company's failing to make the car ready within a 5-hour interval (or less) and driver's canceling the booking once they see their car not ready on the check-in time, we do not know. The information on the time of cancelation decision is not provided, therefore, we only know how late it was when the car has finally returned.
- As seen, there are really few drivers who keeps waiting passed the check-in time.

""")
df = data[data['time_delta_with_previous_rental_in_minutes'].isna() == False]
average_cancel = len(df[df['state']=='canceled']) / len(df) * 100

col1, col2 = st.columns(2)
with col1:
    st.markdown("**Cancelation Rates by Checkin Type**")
    df_n2 = df.groupby('checkin_type')['state'].value_counts(normalize=True)
    df_n2 = df_n2 * 100
    df_n2 = df_n2.rename('percent').reset_index()

    fig = px.bar(df_n2, x='checkin_type', y='percent', color='state', barmode='group')
    fig.add_hline(y=average_cancel, line_dash="dash", line_color="grey")
  
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.markdown("**Cancelation Rates by whether vehicle is late to next checkin**")
    df_n2 = df.groupby('is_late_for_next_checkin')['state'].value_counts(normalize=True)
    df_n2 = df_n2 * 100
    df_n2 = df_n2.rename('percent').reset_index()
    fig = px.bar(df_n2, x='is_late_for_next_checkin', y='percent', color='state', barmode='group')
    fig.add_hline(y=average_cancel, line_dash="dash", line_color="grey")
    st.plotly_chart(fig, use_container_width=True)

st.markdown("""
The figures above again uses only the data from the rentals for which there was an anticipated second 
booking within the 12 hours after previous checkout.
- The first figure shows that cancelation is more common among the drivers using connect 
than drivers who signed mobile contracts. 
- The second figure shows that when the previous driver is late, the likelihood of the next driver
 to cancel is higher than the average cancelation rate amonf the second drivers.
- The dashed line shows the average cancelation late AMONG the drivers whose cars were previously 
rented by another driver.

""")

st.header("Can we minimize the revenue we lose from cancelations due to the delayed returns for the next checkin?")
st.markdown("""
- So far we have seen that customers in average returns cars with an hour delay from the expected checkout that.
- The company in turn tends to provide less than an hour interval between two rentals for approximately 25% of the cases.
- Let's explore how much of those cases could be avoided by setting a threshold time interval.
""")

col1, col2 = st.columns(2)
with col1:
    fig = px.strip(df, x='time_delta_with_previous_rental_in_minutes', y='is_late_for_next_checkin',
                 title='Checkout Delays and Time Delta',
                 labels={'time_delta_with_previous_rental_in_minutes': 'Time Delta between Checkouts', 
                         'is_late_for_next_checkin': 'Is the Previous Renter Late for Checkout'},
                 hover_name='is_late_for_next_checkin', color = 'is_late_for_next_checkin',
                 width=800, height=400)
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("""
By looking at the figure above we can derive that increasing the time interval between two consecutive rentals 
might have indeed decreased the number of returns late for the next check-in in our dataset.
""")

with col2:
    df = data.copy()
    df['is_late_for_next_checkin_binary'] = df['is_late_for_next_checkin'].fillna('not late').apply(lambda x: x if
                                                                                                     x == 'late' else 'not late or no info')
    df = df.groupby(['is_late_for_next_checkin_binary'])['is_late_for_next_checkin_binary'].count().reset_index(name='count')
    fig = px.pie(df, values='count', names='is_late_for_next_checkin_binary')
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("""This figure shows the number of cars that are late for next check-in as 218 which is 1.02 % of all rentals.
    So in our task to find an optimum threshold, we will actually be trying to improve our revenue by 1.02% (if we hold the assumption that
    all cars are equal and have the same rental price) by solving these problematic cases.""")



st.subheader("What should be the optimum threshold and scope ?")
st.markdown("""
The optimization problem we have at hand is the one that trying to maximize the revenue by minimizing the cancelations
arised from vehicles returned too late for the next check-in.

Our goal is to find a threshold and scope such that:
- we will solve the maximum number of problematic cases 
- without creating new problems that can compensate for our gains and diminish the revenue

### First, let's find out how many problematic case can be solved by each threshold and scope:
"""
)
df_pb = data[data['is_late_for_next_checkin'] == 'late']

solved = []
solved_c = []
solved_m = []

for threshold in range(501):
    count = df_pb[df_pb['previous_drivers_delay_in_mins'] < threshold].shape[0]
    count_c = df_pb[(df_pb['checkin_type'] == 'connect') & (df_pb['previous_drivers_delay_in_mins'] < threshold)].shape[0]
    count_m = df_pb[(df_pb['checkin_type'] == 'mobile') & (df_pb['previous_drivers_delay_in_mins'] < threshold)].shape[0]
    solved.append(count)
    solved_c.append(count_c)
    solved_m.append(count_m)

# Convert range to a list for 'x' argument
x_values = list(range(501))

# Create traces for each line
trace1 = go.Scatter(x=x_values, y=solved, mode='lines', name='All cars')
trace2 = go.Scatter(x=x_values, y=solved_c, mode='lines', name='Connect cars')
trace3 = go.Scatter(x=x_values, y=solved_m, mode='lines', name='Mobile cars')

# Create layout for the plot
layout = go.Layout(
    title='Number of problematic cases solved by threshold',
    xaxis=dict(title='Threshold'),
    yaxis=dict(title='Number of cases solved'),
    xaxis_tickvals=list(range(0, 501, 25)),
    legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1)
)

# Create figure and add traces to it
fig = go.Figure(data=[trace1, trace2, trace3], layout=layout)
st.plotly_chart(fig, width = 800, height = 600)

st.markdown("""
- It looks like we are dealing with a curve with diminishing marginal returns, that is, raising the threshold would solve
fewer number of additional problematic cases after each step.
- The curve seems to start flattening around 120, so a quick guess would be to set threshold to 120
minutes and solve around 150 of our problematic cases, right?
- But then why not to set the threshold up to 500 mins and solve all of them?
- ** This is because raising the threshold will come with a price!!**

** Remember : **
- Choosing a threshold interval for making a car available for booking again after its anticipated checkout date 
means that depending on the threshold some of the bookings we had received would not have been authorized in that 
hypothetical threshold.
- Increasing the threshold interval might mean decreasing the availability of our cars, receiving fewer bookings and 
therefore comprimising our revenue.
- Thus, we need to select a threshold such that it would solve the problem of delayed checkouts passing the next 
checkin time, therefore, minimize the cancelations related to it, while at the same time making sure that we are not 
sacrificing much of the potential revenues.

""")

st.subheader("The number of rentals affected by the threshold")
st.markdown("""
Following graph shows the number of rentals that would not have been available for a pick-up at the time demanded by the 
user had we deployed the selected level of minimum threshold when displaying the available cars on our app.
""")
affected_count = []
affected_count_c = []
affected_count_m = []

df_affected = data[data['time_delta_with_previous_rental_in_minutes'].notna()]
df_affected_c = data[(data['checkin_type'] == 'connect') & (data['time_delta_with_previous_rental_in_minutes'].notna())]
df_affected_m = data[(data['checkin_type'] == 'mobile') & (data['time_delta_with_previous_rental_in_minutes'].notna())]

for threshold in range(801):
    count = data[data['time_delta_with_previous_rental_in_minutes'] < threshold].shape[0]
    affected_count.append(count)
    count_c = df_affected_c[df_affected_c['time_delta_with_previous_rental_in_minutes'] < threshold].shape[0]
    affected_count_c.append(count_c)
    count_m = df_affected_m[df_affected_m['time_delta_with_previous_rental_in_minutes'] < threshold].shape[0]
    affected_count_m.append(count_m)

# Create traces for each line
trace1 = go.Scatter(x=list(range(801)), y=affected_count, mode='lines', name='All cars')
trace2 = go.Scatter(x=list(range(801)), y=affected_count_c, mode='lines', name='Connect cars')
trace3 = go.Scatter(x=list(range(801)), y=affected_count_m, mode='lines', name='Mobile cars')

# Create layout for the plot
layout = go.Layout(
    title='Number of rentals that would not have been allowed per threshold',
    xaxis=dict(title='Threshold'),
    yaxis=dict(title='Number of rentals that would not have been allowed'),
    legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1)
)

# Create figure and add traces to it
fig = go.Figure(data=[trace1, trace2, trace3], layout=layout)
st.plotly_chart(fig, width = 800, height = 600)
st.markdown("""
- Looking at the graph above, we can know see why we need to know how much delay in their preferred checkin 
date can customers tolerate, and after which point they 
give up and search for other options.
- For example, we know that the average time delta in our dataset is near 279 minutes but if we decide to select 
this as our threshold just by assuming that it reflects the average preference behavior of customers, we would have unathorized near 1000 of our bookings.
- ** Realize that the problem we have contains a typical trade-off.**
- There is a trade-off between the degree of minutewise flexibility we assume our customers to have and the level
 of threshold we can go for. The less flexible we see them, the more conservative threshold levels we should stick to.

""")

st.subheader('How much flexibility do you think the customers have over their preferred time of pick-up?')
st.markdown("""
Welcome to the fun part ! Let's play with the slider below to select a flexibility interval for the customers and 
then see how many of our bookings we would have lost on each threshold for the flexibility of your choice!
"""
)
flex = st.slider('How many minutes you think users can be flexible about their preferred pick-up time', 0, 800, 10)
affected_count = []
affected_count_c = []
affected_count_m = []


for threshold in range(801):
    count = data[data['time_delta_with_previous_rental_in_minutes'] + flex < threshold].shape[0]
    affected_count.append(count)
    count_c = df_affected_c[df_affected_c['time_delta_with_previous_rental_in_minutes'] + flex < threshold].shape[0]
    affected_count_c.append(count_c)
    count_m = df_affected_m[df_affected_m['time_delta_with_previous_rental_in_minutes'] + flex < threshold].shape[0]
    affected_count_m.append(count_m)

# Create traces for each line
trace1 = go.Scatter(x=list(range(801)), y=affected_count, mode='lines', name='All cars')
trace2 = go.Scatter(x=list(range(801)), y=affected_count_c, mode='lines', name='Connect cars')
trace3 = go.Scatter(x=list(range(801)), y=affected_count_m, mode='lines', name='Mobile cars')

# Create layout for the plot
layout = go.Layout(
    title='Number of rentals that would not have been allowed per threshold',
    xaxis=dict(title='Threshold'),
    yaxis=dict(title='Number of rentals that would not have been allowed'),
    legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1)
)

# Create figure and add traces to it
fig = go.Figure(data=[trace1, trace2, trace3], layout=layout)
st.plotly_chart(fig, width = 800, height = 600) 
st.markdown(
    """
    Let's assume the flexibility of users is 2 hours. Set the slider to 120 minutes.
- Obviously for any threshold below 120 minutes,regardless 
of the scope of our choice, we can keep all our bookings without losing any revenue due to
vsome vehicles becoming non-available since they all would have been within the range of flexibility of our customers.
- In the current dataset, we had 218 problematic case that got cancelled. So any threshold that would require us 
to unauthorize more than 2x218 = 436 rentals makes no sense, 
since even if the threshold had solved all the problematic cancelations, we would have been better-off 
sticking to the current scenario.
- Therefore, we shouldn't probably go for a threshold over 180 minutes if the threshold will be applied to all cars,
 otherwise we would lose more than 436 business - worsened-off than contemporary scenario.
- If we limit our scope to only connect cars, we can go for a threshold of 350 minutes and we would still lose less than 436 of our bookings.
- If we want to apply the feature only to mobile cars, we should stick somewhere around 240 minutes.

Feel free to play with flexibility interval to understand how and why it would affect our business decisions.
    """
)

st.subheader("How many consecutive rentals we would have achieved for a given flexibility interval, threshold, and scope?")
st.markdown("""Notice that no matter how carefully we select the threshold and scope, which group of customers they would
primarily impact ? Is it going to manage to solve more problems ? Or are they going to end up in more customers leaving us?
So, as an example, let's see the counterfactual outcomes of each threshold and scope depending on our flexibility estimates.
- Use again the slider to pick a flexibility interval for customers.
- The graph will use the behavior data of our previous customers, take into account the bookings that we would lose 
also the non-canceled business we might have won due to each threshold and give you an account on how many successful
consecutive rents we would achieve in each scenario.
- Remember the current number of unproblematic consecutive rentals (no cancelation) is 1560.
 """)
item = st.slider('How many minutes users can have flexible about their preferred pick-up time', 0, 720, 10)


fig = go.Figure()

df_affected = data[data['is_late_for_next_checkin'].notna()]
df_affected_c = data[(data['checkin_type'] == 'connect') & (data['is_late_for_next_checkin'].notna())]
df_affected_m = data[(data['checkin_type'] == 'mobile') & (data['is_late_for_next_checkin'].notna())]

not_late_c = len(df_affected_c[df_affected_c['is_late_for_next_checkin'] == 'not late'])
not_late_m = len(df_affected_m[df_affected_m['is_late_for_next_checkin'] == 'not late'])


profit_count = []
profit_count_c = []
profit_count_m = []

for threshold in range(801):
    still_rent = df_affected[df_affected['time_delta_with_previous_rental_in_minutes'] + item >= threshold]
    still_c = df_affected_c[df_affected_c['time_delta_with_previous_rental_in_minutes'] + item >= threshold]
    still_m = df_affected_m[df_affected_m['time_delta_with_previous_rental_in_minutes'] + item >= threshold]

    gain = len(still_rent[
        (still_rent['previous_drivers_delay_in_mins'] < threshold) |
        (still_rent['previous_drivers_delay_in_mins'] < still_rent['time_delta_with_previous_rental_in_minutes'])
    ])

    gain_c = len(still_c[(still_c['previous_drivers_delay_in_mins'] < threshold) |
                         (still_c['previous_drivers_delay_in_mins'] < still_c['time_delta_with_previous_rental_in_minutes'])]) + not_late_m

    gain_m = len(still_m[(still_m['previous_drivers_delay_in_mins'] < threshold) |
                         (still_m['previous_drivers_delay_in_mins'] < still_m['time_delta_with_previous_rental_in_minutes'])]) + not_late_c

    profit_count.append(gain)
    profit_count_c.append(gain_c)
    profit_count_m.append(gain_m)

fig.add_trace(go.Scatter(x=list(range(801)), y=profit_count, mode='lines', name='All cars'))
fig.add_trace(go.Scatter(x=list(range(801)), y=profit_count_c, mode='lines', name='Connect cars'))
fig.add_trace(go.Scatter(x=list(range(801)), y=profit_count_m, mode='lines', name='Mobile cars'))
fig.add_shape(type='line', x0=0, y0=len(data[data['is_late_for_next_checkin'] == 'not late']), x1=600, y1=len(data[data['is_late_for_next_checkin'] == 'not late']),
              line=dict(color='grey', dash='dash'), name='Current Number of Non-problematic Rentals')

fig.update_xaxes(title='Threshold', range=[0, 800], tickvals=list(range(0, 801, 20)))
fig.update_yaxes(title='Number of non-problematic second rentals')
fig.update_layout(title=f'Number of non-problematic second rentals if {item} mins of flexibility', showlegend=True)
st.plotly_chart(fig, use_container_width=True, height = 1000) 
st.markdown("""
## Final remarks on threshold:
- As one can expect all at the threshold 0, all graphs start from the same point which represent the current outcome.
- Until we reach the maximum flexibility interval of customers, the application of the threshold on all cars lead to a steeper increase in the number of successful rentals, which is logical. 
- On the other hand, beyond the maximum flexibility interval of users, it becomes the option that makes business lose customers and money with the highest acceleration. (a steeper decline)
- There are several naive assumptions we have so far made, which does not reflect the real world.
- First, we cannot know the maximum flexibility interval of users for sure, neither will it be shared nor distributed evenly among different groups of users.
- Second, we kept assuming that preventing delay beyond the next check-in time could solve all cancelations by the drivers who canceled in that situation but there is a decent chance that these drivers would have canceled anyway.

#### Therefore:
- Having little knowledge over how flexible the customers are and what percentage of 'late for next check-in' cancelations were actually related to this delay only, it would probably be smarter and safer to limit the scope of the threshold feature to the Connect Cars.
- This way, even in the case we misestimate the flexibility intervals or potential business gains, our loss would not be as dramatic as the all-cars-application scope.
- Another option could be to determine separate thresholds for connect and mobile cars, keeping it lower for connect cars to avoid steep decline in
bookings we will receive in case of misjudgment of customers' flexibility on the pickup time.

""")
st.markdown("---")
            
st.markdown("""
        If you are interested in learning more on this project, check out my [Github](https://github.com/yhaslan) account.
    """)
