import streamlit as st
from pynse import *
import datetime
import matplotlib.pyplot as plt
import mplfinance as mpf
import plotly.express as px

nse=Nse()


def bhavcopy_display():
    with st.sidebar:
        st.write('Bhavcopy Inputs')
        req_date=st.date_input('Select Date',datetime.date.today())
        segment=st.selectbox('Select Segment',['cash','FnO'])

    req_date=None if req_date>=datetime.date.today() else req_date
    
    if segment == "cash":
      bhavcopy=nse.bhavcopy(req_date)
    else:
      bhavcopy=nse.bhavcopy_fno(req_date)
    st.write(f"{segment} bhavcopy for {req_date}")
    st.download_button("Download",bhavcopy.to_csv(),file_name=f"{segment}_bhav_{req_date}.csv")

    st.write(bhavcopy)

def stock_deliv_data():

    with st.sidebar:
      symbol=st.selectbox("Select Symbol",nse.symbols[IndexSymbol.All.name])

      from_Date = st.date_input("From date",datetime.date.today()-datetime.timedelta(30))

      to_date = st.date_input("To Date",datetime.date.today())

    trading_Days = nse.get_hist(from_date=from_Date,to_date=to_date).index
    trading_Days =list(trading_Days.map(lambda x: x.date()))
    data = pd.DataFrame()

    for date in trading_Days:
        try:
            bhav = nse.bhavcopy(date).loc[symbol]  
            bhav.set_index("DATE1",inplace=True)
            data = data.append(bhav)
        except Exception as e:
            print(f"error {e} for {date}")

    data = data.astype(float)
    data.index = data.index.map(pd.to_datetime)
    data = data[
           [
              "OPEN_PRICE",
              "HIGH_PRICE",
              "LOW_PRICE",
              "CLOSE_PRICE",
              "TTL_TRD_QNTY",
              "DELIV_QTY",
              "DELIV_PER" ,
           ]
    ] 
    data.columns = "open high low close volume deliv_qty deliv_per".split()
    
    deliv_data = [mpf.make_addplot(data["deliv_per"], ylabel="deliv %")]
      
    fig, ax=mpf.plot(
        data,
        addplot= deliv_data ,
        type="candle",
        style="yahoo",
        volume=True,
        returnfig=True,
        title=f"{symbol} Delivery %",
        figratio=(16, 7),
        figscale=1.2,
      )

    st.write(fig) 
    st.write(data)

def high_low_deliv():
  with st.sidebar:
    req_date = st.date_input("Select Date",datetime.date.today())
    sort_by = st.radio("Sort By",["Highest","Lowest"])

    index_name = st.selectbox("Index",[i.name for i in IndexSymbol])
    no_of_stocks = st.number_input("No of Stocks",step=1,min_value=10)

  req_date=None if req_date>=datetime.date.today() else req_date

  bhavcopy = nse.bhavcopy(req_date)  

  bhavcopy = bhavcopy.reset_index(level=1)

  bhavcopy = bhavcopy[
           [             
              "OPEN_PRICE",
              "HIGH_PRICE",
              "LOW_PRICE",
              "CLOSE_PRICE",
              "TTL_TRD_QNTY",
              "DELIV_QTY",
              "DELIV_PER" ,
           ]
           ]

  bhavcopy=bhavcopy.sort_values('DELIV_PER',ascending=True if sort_by=='Lowest' else False)
  bhavcopy=bhavcopy[bhavcopy.index.isin(nse.symbols[index_name])]
  st.write(bhavcopy.head(int(no_of_stocks)))





analysis_dict = {"Bhavcopy": bhavcopy_display,
                 "Stock Delivery Data":stock_deliv_data,
                 "High/Low Delivery":high_low_deliv
} 

with st.sidebar:
      selected_anlysis=st.radio("Select Analysis",list(analysis_dict.keys()))   
      st.write("---")

st.header(selected_anlysis)

analysis_dict[selected_anlysis]()
