import React from 'react';

import { Modal } from './styles';

import {Close} from '../../components/Icons'

export default ({title, component, setModalVisible}) => {
  return (
      <Modal>
        <div className='container'>
          <div className='header'>
            <p>{title}</p>
            <div className='close' onClick={() => setModalVisible(false)}>
              <Close color={'black'} />
            </div>
          </div>
          
          {component}

        </div>
      </Modal>
  );
}
