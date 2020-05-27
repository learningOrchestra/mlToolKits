import React from 'react';

import { Card } from '../../constants/StyledComponents';
import { Container } from './styles';

import { Add } from '../../components/Icons';

export default ({add=false, projectName, handleOnClick}) => {
  return (
    <Container onClick={handleOnClick}>
      <Card width={156} height={140}>
          {
            add ?
            <div className='container-add-project'>
              <Add color={'var(--color-primary)'}/>
              <p>Add project</p>
            </div>
            :
            <div className='container-project'>
              <p>{projectName}</p>
            </div>
          }
      </Card>
    </Container>
  );
}