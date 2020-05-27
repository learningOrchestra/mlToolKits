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
    width: 50%;
    min-height: 90%;
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

  div.input-file {
    display: flex;
    justify-content: space-between;
    align-items: center;
    width: 90%;
    padding: 32px 0;
  }

  #input-file {
    width: 300px;
    background-color: white;
  }

  div.close {
    position: relative;
    right: -4.5%;
    /* padding: 8px; */
  }

  div.close:hover {
    cursor: pointer;
    opacity: .4;
  }
`;
