import React from 'react'
import {Switch, Route, Redirect} from 'react-router-dom'

import Projects from './pages/Projects'
import Dashboard from './pages/Dashboard'
import Workflow from './pages/Workflow'
import DataQueue from './pages/DataQueue'

export default () => {
    return (
      <Switch>
        <Route exact path="/" component={Projects}/>
        <Route exact path="/dashboard" component={Dashboard}/>
        <Route exact path="/workflow" component={Workflow}/>
        <Route exact path="/data" component={DataQueue}/>
        <Redirect from ="*" to="/"/>
      </Switch>
    )
}
