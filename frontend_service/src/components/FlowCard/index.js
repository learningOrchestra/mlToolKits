import React, {useState} from 'react';

import { Container, Card, Line, Button } from './styles';

import Modal from '../../components/Modal'
import ModalAddData from '../../components/ModalAddData'

export default ({positionX, positionY, data, flowData, setFlowData}) => {
  const [modalVisible, setModalVisible] = useState(false);

  function handleAddCard() {
    setModalVisible(true)
  }

  const addData = (<ModalAddData flowData={flowData} setFlowData={setFlowData} setModalVisible={setModalVisible} />)

  return (
    <>
      {
        modalVisible ?
          <Modal title={'Data'} component={addData} setModalVisible={setModalVisible} />
        : null
      }
      
      <Container positionX={positionX} positionY={positionY} data className={data.type}>
        <Card color={data.color}><p>{data.name}</p></Card>
        {
          data.final ? 
          <>
            <Line size={48} color={data.color} />
            <Button onClick={handleAddCard} color={data.color}>
              <p>+</p> 
            </Button>
          </>
          : <Line size={112} color={data.color}/>
        }
      </Container>
    </>
  );
}
