import React, { useState, useEffect } from 'react';
import Navbar from '../components/Navbar';
import api from '../services/api';

function APIKeyPage() {
    const [apiKey, setApiKey] = useState('');
    const [accountId, setAccountId] = useState('');
    const [currentKey, setCurrentKey] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchKey = async () => {
            try {
                // L'API renvoie une liste, on prend le premier élément
                const response = await api.get('/keys/');
                if (response.data.length > 0) {
                    const key = response.data[0];
                    setCurrentKey(key);
                    // On ne remplit pas les champs pour des raisons de sécurité
                }
            } catch (error) {
                console.error('Failed to fetch API key', error);
            }
            setLoading(false);
        };
        fetchKey();
    }, []);

    const handleSubmit = async (e) => {
        e.preventDefault();
        const data = { oanda_api_key: apiKey, oanda_account_id: accountId };
        try {
            if (currentKey) {
                // Mettre à jour la clé existante
                await api.put(`/keys/${currentKey.id}/`, data);
            } else {
                // Créer une nouvelle clé
                await api.post('/keys/', data);
            }
            alert('API Key saved successfully!');
        } catch (error) {
            console.error('Failed to save API key', error);
            alert('Error saving API key.');
        }
    };

    if (loading) {
        return <div>Loading...</div>;
    }

    return (
        <div>
            <Navbar />
            <h1>Manage OANDA API Key</h1>
            <form onSubmit={handleSubmit}>
                <p>
                    {currentKey 
                        ? `An API key is configured for account ${currentKey.oanda_account_id}.` 
                        : 'No API key is configured.'}
                </p>
                <p>Enter your key below to add or update it. The key is encrypted before being stored.</p>
                
                <input 
                    type="text" 
                    value={accountId}
                    onChange={(e) => setAccountId(e.target.value)}
                    placeholder="OANDA Account ID"
                    required
                />
                <input 
                    type="password" // Type password pour masquer la clé
                    value={apiKey}
                    onChange={(e) => setApiKey(e.target.value)}
                    placeholder="OANDA API Key"
                    required
                />
                <button type="submit">Save API Key</button>
            </form>
        </div>
    );
}

export default APIKeyPage;
