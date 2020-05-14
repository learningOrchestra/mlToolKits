import styled from 'styled-components'

export const Queue = styled.div`
  width: 100%;
  padding: 32px;

  p.title {
    font-size: 20px;
    font-weight: 500px
  }

  div.container-add-file {
    display: flex;
    justify-content: space-between;
    margin: 16px 0;
  }

  div.container-add-file input {
    width: calc(100vw / 6);
    font-size: 14px;
  }

  div.container-add-file button {
    width: calc(100vw / 14);
  }

  div.container-file-table {
    padding-top: 16px;
  }

  div.container-file-table .header,
  div.container-file-table .row {
    display: flex;
  }

  div.row,
  div.header {
    display: flex;
    align-items: center;
  }

  div.header p {
    font-size: 14px;
    font-weight: bold;
    padding: 16px 0;
  }

  div.row p {
    font-size: 14px;
    font-weight: 400;
    padding: 16px 0;
  }

  p.file {
    width: 10%;
  }

  p.name {
    width: 40%;
  }

  p.size {
    width: 15%;
  }

  p.status {
    width: 20%;
  }

`;