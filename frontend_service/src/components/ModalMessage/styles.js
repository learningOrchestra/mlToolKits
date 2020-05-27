import styled from 'styled-components'

export const Modal = styled.div`
  display: flex;
  justify-content: center;
  align-items: center;
  position: absolute;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background-color: #00000090;
  z-index: 10;

  div.container {
    display: flex;
    flex-direction: column;
    align-items: center;
    width: 30%;
    padding-bottom: 32px;
    background-color: white;
    opacity: 1;
    border-radius: 4px;
  }

  div.header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    width: 90%;
    height: 40px;
  }

  div.header p {
    font-weight: bold;
    margin-top: 32px;
    font-size: 20px;
  }

  div.close {
    position: relative;
    right: -4.5%;
  }

  div.close:hover {
    cursor: pointer;
    opacity: .4;
  }

  p.message-text {
    margin-top: 32px;
    font-weight: 300;
  }

  div.buttons {
    display: flex;
    justify-content: space-between;
    align-items: center;
    width: 50%;
    margin-top: 32px;
  }
`;
