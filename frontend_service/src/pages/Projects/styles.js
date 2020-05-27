import styled from 'styled-components'

export const Container = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;

  div.container-text {
    display: flex;
    justify-content: flex-start;
    width: calc(172px*3);
    margin-top: 64px;
    margin-bottom: 40px;

    font-size: 18px;
    font-weight: 500;
    color: var(--color-secondary)
  }

  div.container-projects {
    display: flex;
    width: calc(172px*3);
    flex-wrap: wrap;
    justify-content: flex-start;
    align-items: center;
  }

  hr {
    width: calc(172px * 3);
    margin: 32px 0;
    border-color: var(--color-support-primary);
  } 
`;