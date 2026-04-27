import React from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import Home from './components/Home';
import Login from './components/Login';
import Signup from './components/Signup';
import BuildingForm from './components/BuildingForm';
import PresentDomains from './components/PresentDomains';
import ServicesApplications from './components/ServicesApplications';
import Profile from './components/Profile';
import MyBuildings from './components/MyBuildings';
import SRIScore from './components/SRIScore';
import UpgradeSRI from './components/UpgradeSRI';

function App() {
    return (
        <Router>
            <Routes>
                <Route path="/" element={<Home />} />
                <Route path="/login" element={<Login />} />
                <Route path="/signup" element={<Signup />} />
                <Route path="/profile" element={<Profile />} />
                <Route path="/my_buildings" element={<MyBuildings />} />
                <Route path="/add_building" element={<BuildingForm />} />
                <Route path="/present_domains" element={<PresentDomains />} />
                <Route path="/services_applications" element={<ServicesApplications />} />
                <Route path="/sri_score/:buildingId" element={<SRIScore />} />
                <Route path="/upgrade_sri/:buildingId" element={<UpgradeSRI />} />
            </Routes>
        </Router>
    );
}

export default App;
