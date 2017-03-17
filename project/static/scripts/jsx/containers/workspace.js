//COMPONENTS
import React from 'react';
import ReactDOM from 'react-dom';
import thunkMiddleware from 'redux-thunk'
import createLogger from 'redux-logger'
import { Provider } from 'react-redux';
import {createStore, applyMiddleware} from 'redux';

import workspaceState from '../reducers/rootReducer';
import ViewContainer from './viewContainer';
import Toolbar from '../components/toolbar';
import {fetchComparison} from '../actions/actions';

// const initialState = {
//     view: 'CHART',
//     attributes: [
//         {id: 1, name: "size", type_id: 0},
//         {id: 2, name: "color", type_id: 0},
//         {id: 3, name: "number", type_id: 1}
//     ],
//     items: [
//         {name: "ball 2", "1": "large", "2": "red", "3": -1.32},
//         {name: "ball 3", "1": "small", "2": "blue", "3": 3},
//         {name: "ball 4", "1": "medium", "2": "green", "3": 8.22}
//     ]
// }

// Grab DOM element to replace.
var workspaceElem = document.getElementById("workspace");

// Pull data from jinja injection and parse as JSON
var initialState = JSON.parse(workspaceElem.dataset.comparison);

// Load data into initial state for Redux
initialState = {present: {...initialState, view: 'CHART'}};

// Set up logger
const loggerMiddleware = createLogger();

// Make store and reducers along with Middleware setup
const store = createStore(workspaceState, initialState,
    applyMiddleware(
        thunkMiddleware,
        loggerMiddleware
    ));

// Dispatch action to fetch the comparison
//store.dispatch(fetchComparison());

class Workspace extends React.Component {
    render() {
        return (
            <div id="wrapper">
                <Toolbar/>
                <ViewContainer/>
            </div>
        );
    }
}

// ========================================



ReactDOM.render(
    <Provider store={store}>
        <Workspace/>
    </Provider>,
    workspaceElem
);