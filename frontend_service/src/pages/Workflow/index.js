import React from 'react';

import { Main } from '../../constants/StyledComponents';
import { Container, AppBar } from './styles';

import Flow from '../../components/Flow';

export default () => {
  return (
    <Main withoutBackground='true'>
      <Container>
        <AppBar>
        </AppBar>

        <Flow />

      </Container>
    </Main>
  );
}