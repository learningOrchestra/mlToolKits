import styled from 'styled-components'

export const Container = styled.div`
  padding: 8px;

  div:hover {
    cursor: pointer;
  }

  div.container-project {
    width: 100%;
    height: 100%;
  }

  div.container-project p {
    color: var(--color-typography);
    margin: 16px 8px;
    font-size: 14px;
    font-weight: 500;
  }
  
  div.container-add-project {
    width: 100%;
    height: 100%;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
  }

  div.container-add-project p {
    color: var(--color-primary);
    margin-top: 8px;
    font-size: 14px;
    font-weight: 500;
  }
`;