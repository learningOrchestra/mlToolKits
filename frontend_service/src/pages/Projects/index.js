import React from 'react';
import { useHistory } from "react-router-dom";

import { Main, Wrapper } from '../../constants/StyledComponents';
import { Container } from './styles';

import CardProjectHome from '../../components/CardProjectHome';

const projects = [
  {name: 'Awesome Project'}, 
  {name: 'Project'},
  {name: 'Learning Project'},
  {name: 'My Project'},
  {name: 'First Project'},
]

export default () => {
  let history = useHistory();

  function handleOnClickCardProject() {
    history.push("/dashboard");
  }

  return (
    <Main>
      <Wrapper>
        <Container>
            <div className='container-text'>
              <p>Your learningOrchestra projects</p>
            </div>
            
            <div className='container-projects'>
              <CardProjectHome add />
              {
                projects.map((project, index) => 
                  <CardProjectHome 
                    key={index} 
                    projectName={project.name} 
                    handleOnClick={handleOnClickCardProject}
                  />
                )
              }
            </div>
            <hr></hr>
        </Container>
      </Wrapper>
    </Main>
  );
}