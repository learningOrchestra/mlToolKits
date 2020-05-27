import styled from 'styled-components'

const cardWidth = 192
const cardHeight = 96
const buttonWidth = 48
const buttonHeight = 48

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
    width: 50%;
    height: 80%;
    background-color: white;
    opacity: 1;
  }

  div.header {
    display: flex;
    justify-content: flex-end;
    align-items: center;
    width: 100%;
    height: 40px;
    padding-right: 8px;
  }

  div.input-file {
    width: 100%;
    padding: 16px 32px;
  }

  #input-file {
    width: 300px;
    background-color: white;
  }

  div.close:hover {
    cursor: pointer;
    opacity: .4;
  }
`;

export const Container = styled.div`
  display: flex;
  justify-content: center;
  align-items: center;
  width: ${() => `${cardWidth + buttonWidth + 64}px`};
  height: ${() => `${cardHeight}px`};
  position: relative;
  top: ${props => `${props.positionY}px`};
  left: ${props => `${props.positionX}px`};

  &.data {
    cursor: pointer;
  }
`;

export const Card = styled.div`
  display: flex;
  justify-content: center;
  align-items: center;
  width: ${() => `${cardWidth}px`};
  height: ${() => `${cardHeight}px`};
  background-color: white;
  border: 2px solid ${props => `${props.color}`};
  border-radius: 5px;
`;

export const Line = styled.div`
  width: ${props => `${props.size}px`};
  height: 2px;
  background-color: ${props => `${props.color}`};
`;

export const Button = styled.div`
  display: flex;
  justify-content: center;
  align-items: center;
  width: ${() => `${buttonWidth}px`};
  height: ${() => `${buttonHeight}px`};
  margin-right: 16px;
  background-color: ${props => `${props.color}`};
  border-radius: 32px;

  p {
    font-size: 24px;
    color: white;
  }

  &:hover {
    cursor: pointer;
    opacity: .8;
  }
`;