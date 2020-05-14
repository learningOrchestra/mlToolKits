import styled from 'styled-components'

export const Card = styled.div`
  width: ${props => `${props.width}px`};
  height: ${props => `${props.height}px`};
  background-color: var(--color-secondary);
  border: 1px solid var(--color-support-secondary);
  box-shadow: 0px 4px 4px rgba(0, 0, 0, 0.25);
  border-radius: 4px;
  margin: ${props => `${props.margin}`};
`;

export const Main = styled.main`
  display: flex;
  justify-content: center;
  min-height: 100vh;
  width: 100vw;
  padding-left: calc(100vw / 5);
  background: linear-gradient(var(--color-primary) 33vh, var(--color-background) 33vh);
`;

export const Wrapper = styled.div`
  width: calc(100vw / 2);
`;
