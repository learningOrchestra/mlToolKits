import React, { useState, useEffect } from 'react';
import FormControl from '@material-ui/core/FormControl';
import InputLabel from '@material-ui/core/InputLabel';
import MenuItem from '@material-ui/core/MenuItem';
import Select from '@material-ui/core/Select';
import Button from '@material-ui/core/Button';

import Table from '../../components/Table'

import api from '../../services/api'

export default ({flowData, setFlowData, setModalVisible}) => {
  const [filename, setFilename] = useState('');
  const [files, setFiles] = useState([]);
  const [dataTable, setDataTable] = useState(null);

  useEffect( () => {
    (async () => {
      const {data} = await api.get('/files')
      const _files = data.result.filter(value => value.finished).map(value => value.filename)
      setFiles(_files)
    })()
  }, [])

  async function handleChangeFile(event) {
    const _filename = event.target.value
    
    if (!_filename) {
      setFilename('')
      setDataTable(null)
      return 
    }

    const params = { 
      "filename": _filename,
      "skip": 0,
      "limit": 10,
      "query": {"_id": { "$ne": 0 }}
    }
    const {data} = await api.get('/files', {params})
    
    setDataTable(data)
    setFilename(_filename)
  }

  function handleAddFile() {
    if (!dataTable) return
    
    const _data = {
      name: filename, 
      type: 'data', 
      color: '#30B700', 
      final: true
    }

    flowData.map(data => data.final = false)

    setFlowData([...flowData, _data])

    setModalVisible(false)
  }

  return (  
    <>        
      <div className='input-file'>
        <FormControl variant="outlined" size='small'>
          <InputLabel id="input-file-label">Filename</InputLabel>
          <Select
            labelId="input-file-label"
            id="input-file"
            value={filename}
            onChange={event => handleChangeFile(event)}
            label="Filename"
          >
            <MenuItem value="">
              <em>None</em>
            </MenuItem>
            {files.map((value, index) => 
              <MenuItem key={index} value={value}>{value}</MenuItem>
            )}
          </Select>
        </FormControl>

        <Button 
          variant="contained" 
          color="primary" 
          onClick={handleAddFile}
        >
          Add Data
        </Button>
      </div>

      { dataTable ? <Table data={dataTable} /> : null }
    </>
  );
}
