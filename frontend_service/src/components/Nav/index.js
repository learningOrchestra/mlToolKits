import React, {useState, useEffect} from 'react';
import { useLocation } from 'react-router-dom';

import { Nav, NavItem } from './styles';

import {Profile, Notification, Home, Settings, Help} from '../Icons'
import {Workflow, Data, Function} from '../Icons'

export default () => {
  const [isHome, setIsHome] = useState(true)
  const location = useLocation();

  useEffect(() => {
    const _isHome = location.pathname === '/';
    setIsHome(_isHome) 
  }, [location]);


  return (
    <Nav>
      <NavItem href="#">
        <Profile size={32} /> 
        <p>User Name</p>
        {/* <Notification />  */}
      </NavItem>
      
      <hr></hr>

      {
        isHome ?
          <>
            <NavItem href="#">
              <Home /> 
              <p>Home</p>
            </NavItem>
            <NavItem href="#">
              <Settings /> 
              <p>Settings</p>
            </NavItem>
            <NavItem href="#">
              <Help /> 
              <p>Help</p>
            </NavItem>
          </>
        :
          <>
            <NavItem href="/dashboard">
              <Home /> 
              <p>Project Overview</p>
            </NavItem>
            <NavItem href="/workflow">
              <Workflow /> 
              <p>Workflow</p>
            </NavItem>
            <NavItem href="/data">
              <Data /> 
              <p>Data</p>
            </NavItem>
            <NavItem href="#">
              <Function /> 
              <p>Functions</p>
            </NavItem>
            <NavItem href="#">
              <Help /> 
              <p>Help</p>
            </NavItem>
          </>
      }
    </Nav>
  );
}