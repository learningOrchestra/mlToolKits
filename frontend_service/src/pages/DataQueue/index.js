import React from 'react';

import {Main, Wrapper, Card} from '../../constants/StyledComponents';
import Queue from '../../components/Queue';

import api from '../../services/api'

const files = [
  {type: 'json', name: 'file_name_000.json', size:'16 MB', status:'Sent'},
  {type: 'csv', name: 'file_name_001.csv', size:'32 MB', status:'Sent'},
  {type: 'json', name: 'file_name_001.json', size:'64 MB', status:'Error'},
  {type: 'json', name: 'file_name_003.json', size:'128 MB', status:'Sending'},
  {type: 'csv', name: 'file_name_002.csv', size:'256 MB', status:'In queue'},
  {type: 'csv', name: 'file_name_000.csv', size:'512 MB', status:'In queue'},
  {type: 'json', name: 'file_name_002.json', size:'1 GB', status:'In queue'},
]

export default () => {
  async function handleSubmit(fileName, url) {
    const data = {"filename": fileName, "url": url}
    api.post('/add', data)
  }

  return (
    <Main>
      <Wrapper>
        <Card margin={'64px 0'}>
          <Queue title={'Data'} handleSubmit={handleSubmit} files={files}/>
        </Card>
      </Wrapper>
    </Main>
  );
}