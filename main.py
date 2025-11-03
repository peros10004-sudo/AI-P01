import streamlit as st
st.title('나의 첫 웹 서비스 만들기!!')
name=st.text_input('이름을 입력하세요:')
st.selectbox('좋아하는 음식을 선택해주세요:',['김치찌개','된장찌개'])
if st.button('인사말생성'):
  st.info(menu+'를 좋아하시나봐요! 저도 좋아해요!')
  st.error('반가워요')
  st.balloons()
  
