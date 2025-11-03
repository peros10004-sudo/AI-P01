import streamlit as st
st.title('나의 첫 웹 서비스 만들기!!')
st.text_input('이름을 입력하세요:')
if st.button('인사말생성'):
  st.write(name+_'님! 안녕하세요')

