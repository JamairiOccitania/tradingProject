import React from 'react';
import Navbar from '../components/Navbar';

function DashboardPage() {
    return (
        <div>
            <Navbar />
            <h1>Dashboard</h1>
            <p>Welcome to your trading platform.</p>
            {/* Ici, nous ajouterons plus tard des infos comme le capital, etc. */}
        </div>
    );
}

export default DashboardPage;
