import React, { useState, useEffect } from 'react';
import api from '../services/api';
import Navbar from '../components/Navbar';

const BacktestingPage = () => {
    const [backtests, setBacktests] = useState([]);
    const [newBacktest, setNewBacktest] = useState({
        asset: 'EUR_USD',
        strategy: 'rsi_sma',
        start_date: '',
        end_date: '',
        parameters: '{"rsi_period": 14, "sma_period": 50}',
    });
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');

    useEffect(() => {
        fetchBacktests();
    }, []);

    const fetchBacktests = async () => {
        try {
            const response = await api.get('/backtests/');
            setBacktests(response.data);
        } catch (err) {
            setError('Failed to fetch backtests.');
        }
    };

    const handleInputChange = (e) => {
        const { name, value } = e.target;
        setNewBacktest({ ...newBacktest, [name]: value });
    };

    const handleFormSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError('');
        try {
            await api.post('/backtests/', newBacktest);
            fetchBacktests(); // Refresh the list
            setNewBacktest({
                asset: 'EUR_USD',
                strategy: 'rsi_sma',
                start_date: '',
                end_date: '',
                parameters: '{"rsi_period": 14, "sma_period": 50}',
            });
        } catch (err) {
            setError('Failed to start backtest. Check the parameters.');
        } finally {
            setLoading(false);
        }
    };

    const renderResult = (result) => {
        if (!result) return 'N/A';
        if (result.error) return <span style={{ color: 'red' }}>{result.error}</span>;
        return (
            <ul>
                <li>Profit/Loss: {result.profit_loss}</li>
                <li>Total Trades: {result.total_trades}</li>
                <li>Win Rate: {result.win_rate}%</li>
                <li>Final Balance: {result.final_balance}</li>
            </ul>
        );
    };

    return (
        <div>
            <Navbar />
            <div className="container">
                <h2>Backtesting</h2>
                
                <div className="card">
                    <h3>Run New Backtest</h3>
                    {error && <p className="error">{error}</p>}
                    <form onSubmit={handleFormSubmit}>
                        <input
                            type="text"
                            name="asset"
                            value={newBacktest.asset}
                            onChange={handleInputChange}
                            placeholder="Asset (e.g., EUR_USD)"
                            required
                        />
                        <input
                            type="date"
                            name="start_date"
                            value={newBacktest.start_date}
                            onChange={handleInputChange}
                            required
                        />
                        <input
                            type="date"
                            name="end_date"
                            value={newBacktest.end_date}
                            onChange={handleInputChange}
                            required
                        />
                        <select name="strategy" value={newBacktest.strategy} onChange={handleInputChange}>
                            <option value="rsi_sma">RSI + SMA</option>
                        </select>
                        <textarea
                            name="parameters"
                            value={newBacktest.parameters}
                            onChange={handleInputChange}
                            placeholder='Parameters (JSON format)'
                        />
                        <button type="submit" disabled={loading}>
                            {loading ? 'Starting...' : 'Run Backtest'}
                        </button>
                    </form>
                </div>

                <h3>Backtest History</h3>
                <ul className="list">
                    {backtests.map(bt => (
                        <li key={bt.id}>
                            <strong>{bt.asset}</strong> ({bt.strategy})<br />
                            <small>{new Date(bt.start_date).toLocaleDateString()} to {new Date(bt.end_date).toLocaleDateString()}</small><br />
                            Status: <strong>{bt.status}</strong>
                            <div>
                                <h4>Results</h4>
                                {renderResult(bt.result)}
                            </div>
                        </li>
                    ))}
                </ul>
            </div>
        </div>
    );
};

export default BacktestingPage;
