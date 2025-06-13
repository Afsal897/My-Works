import {BrowserRouter as Router , Routes, Route} from 'react-router-dom'
import Login from './pages/login'
import Home from './pages/home/home'
import Register from './pages/register'
import ProtectedRoute from './components/protectedroute'
import Logout from './pages/logout'
import AddProduct from './pages/home/addproduct'
import Profile from './pages/home/profile'



function App() {

  return (
    <>
    <Router>
      <Routes>
        <Route path='/*' element={< Login/>}/>
        <Route path='/register' element={< Register/>}/>
        <Route element={<ProtectedRoute />}>
        <Route path='/home' element={ < Home/>}/>
        <Route path='/home/add_product' element={ < AddProduct/>}/>
        <Route path='/profile' element={<Profile/>}/>
        <Route path='/logout' element={<Logout/>}/>
        </Route>
      </Routes>
    </Router>
    </>
  )
}

export default App
