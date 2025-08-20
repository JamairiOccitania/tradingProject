import React, { useState, useEffect } from 'react';
import Navbar from '../components/Navbar';
import api from '../services/api';

function BotsPage() {
    const [bots, setBots] = useState([]);

    useEffect(() => {
        const fetchBots = async () => {
            try {
                const response = await api.get('/bots/');
                setBots(response.data);
            } catch (error) {
                console.error('Failed to fetch bots', error);
            }
        };
        fetchBots();
    }, []);

    return (
        <div>
            <Navbar />
            <h1>My Bots</h1>
            <ul>
                {bots.map(bot => (
                    <li key={bot.id}>
                        {bot.name} ({bot.asset}) - {bot.status}
                    </li>
                ))}
            </ul>
            {/* Ici, nous ajouterons un formulaire pour créer de nouveaux bots */}
        </div>
    );
}

export default BotsPage;
