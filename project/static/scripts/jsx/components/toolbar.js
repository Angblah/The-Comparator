import React from 'react';
import {connect} from 'react-redux'
import {addAttr, addItem, changeView} from '../actions/actions'
import { ActionCreators as UndoActionCreators } from 'redux-undo'

class Toolbar extends React.Component {
    render() {
        if (this.props.view === 'CHART') {
            return (
                <div>
                    <div className="btn-toolbar d-flex justify-content-start" role="toolbar" aria-label="Toolbar with button groups">
                        <div className="btn-group mr-2" role="group" aria-label="First group">
                            <button type="button" className="btn btn-secondary" id="addAttrButton" onClick={() => this.props.addAttr(12)}>Add Attribute</button>
                            <button type="button" className="btn btn-secondary" id="addItemButton" onClick={() => this.props.addItem(12)}>Add Item</button>
                        </div>

                        <div className="btn-group mr-2" role="group" aria-label="Second group">
                            <button onClick={this.props.onUndo} disabled={!(this.props.canUndo)}>
                              Undo
                            </button>
                            <button onClick={this.props.onRedo} disabled={!(this.props.canRedo)}>
                              Redo
                            </button>
                        </div>

                        <div className="btn-group mr-2" role="group" aria-label="Third group">
                            <button id="toggleViewButton" className="btn btn-primary" onClick={() => this.props.changeView('SPIDER')}>Toggle View</button>
                        </div>

                        <div className="btn-group ml-auto" role="group" aria-label="Export/Share">
                            <button type="button blank-bg" className="btn btn-secondary">Share/Export</button>
                        </div>
                    </div>
                </div>
            );
        } else {
            return (
                <div className="btn-toolbar d-flex justify-content-start" role="toolbar" aria-label="Toolbar with button groups">
                    <div className="btn-group mr-2" role="group" aria-label="Third group">
                        <button id="toggleViewButton" className="btn btn-primary" onClick={() => this.props.changeView('CHART')}>Toggle View</button>
                    </div>
                </div>
            );
        }
    }
}

const mapStateToProps = (state) => {
    return {
        view: state.present.view,
        canUndo: state.past.length > 0,
        canRedo: state.future.length > 0
    };
}

const mapDispatchToProps = (dispatch, ownProps) => {
    return {
        addAttr: (compId) => {
            dispatch(addAttr(compId))
        },
        addItem: (compId) => {
            dispatch(addItem(compId))
        },
        changeView: (view) => {
            dispatch(changeView(view))
        },
        onUndo: () => dispatch(UndoActionCreators.undo()),
        onRedo: () => dispatch(UndoActionCreators.redo())
    }
}

export default connect(
    mapStateToProps,
    mapDispatchToProps
)(Toolbar)