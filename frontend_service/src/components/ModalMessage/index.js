import React from 'react';
import Button from '@material-ui/core/Button';

import { Modal } from './styles';

import {Close} from '../../components/Icons'

export default ({title, message, setModalVisible, handleOnConfirm}) => {
  return (
      <Modal>
        <div className='container'>
          <div className='header'>
            <p>{title}</p>
            <div className='close' onClick={() => setModalVisible(false)}>
              <Close color={'black'} />
            </div>
          </div>
          
          <p className={'message-text'}>{message}</p>

          <div className={'buttons'}>
            <Button variant="contained" color="default" onClick={() => setModalVisible(false)}>Cancel</Button>
            <Button variant="contained" color="primary" onClick={handleOnConfirm}>Confirm</Button>
          </div>
        </div>
      </Modal>
  );
}
