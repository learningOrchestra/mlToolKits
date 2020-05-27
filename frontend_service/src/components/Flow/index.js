import React, { useEffect, useState } from 'react';

import { Container, FlowContainer } from './styles';

import FlowCard from '../FlowCard';

export default () => {
  const [flowData, setFlowData] = useState([{name: 'Awesome Project', type: 'project', color: '#2196F3', final: true}]);

  useEffect(() => {
  }, [])

  return (
    <Container>
      <FlowContainer>
        {flowData.map((data, index) =>
           <FlowCard 
            positionX={32+(304*index)} 
            positionY={32*-(3*index)} 
            data={data} 
            flowData={flowData}
            setFlowData={setFlowData}
          />
        )}
      </FlowContainer>
    </Container>
  );
}
