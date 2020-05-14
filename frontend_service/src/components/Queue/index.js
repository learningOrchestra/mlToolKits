import React, { useState } from 'react';
import TextField from '@material-ui/core/TextField';
import Button from '@material-ui/core/Button';

import {Queue} from './styles';

import {File} from '../../components/Icons';

export default ({title, handleSubmit, files}) => {
  const [fileName, setFileName] = useState('');
  const [url, setUrl] = useState('');

  return (
    <Queue>
      <p className='title'>{title}</p>

      <div className='container-add-file'>
        <TextField 
          label="File name" 
          variant="outlined" 
          size="small"
          onChange={event => setFileName(event.target.value)}
        />
        <TextField 
          label="URL" 
          variant="outlined" 
          size="small" 
          onChange={event => setUrl(event.target.value)}
        />
        <Button 
          variant="contained" 
          color="primary" 
          onClick={() => handleSubmit(fileName, url)}
        >
          Send
        </Button>
      </div>

      <div className='container-file-table'>
        <div className='header'>
          <p className='file'>File</p>
          <p className='name'>Name</p>
          <p className='size'>Size</p>
          <p className='status'>Status</p>
        </div>
      
          {files.map((file, index) => 
            <div key={index} className='row'>
              <p className='file'><File /></p>
              <p className='name'>{file.name}</p>
              <p className='size'>{file.size}</p>
              <p className='status'>{file.status}</p>
            </div>
          )}

      </div>
    </Queue>
  );
}