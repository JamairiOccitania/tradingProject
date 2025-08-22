import React, { useState, useEffect } from 'react';
import {
  Stack,
  Title,
  Card,
  Text,
  Group,
  Badge,
  Button,
  Modal,
  TextInput,
  Select,
  NumberInput,
  Grid,
  ActionIcon,
  Table,
  Loader,
  Center,
  Alert,
  Switch
} from '@mantine/core';
import {
  IconPlus,
  IconPlayerPlay,
  IconPlayerStop,
  IconSettings,
  IconTrash,
  IconRobot,
  IconAlertCircle
} from '@tabler/icons-react';
import { useForm } from '@mantine/form';
import { notifications } from '@mantine/notifications';
import api from '../services/api';

function BotsPage() {
  const [bots, setBots] = useState([]);
  const [loading, setLoading] = useState(true);
  const [modalOpened, setModalOpened] = useState(false);
  const [editingBot, setEditingBot] = useState(null);
  const [brokerCredentials, setBrokerCredentials] = useState([]);

  const form = useForm({
    initialValues: {
      name: '',
      asset: 'XAU_USD',
      broker: 'oanda',
      strategy: 'RSI_SMA',
      rsi_period: 14,
      sma_period: 50,
      tp: 0.05,
      sl: 0.02,
      position_size: 100,
      mode: 'paper',
      use_trailing_stop: false,
      trailing_distance: 0.02,
      use_dynamic_sizing: false,
      position_sizing_method: 'fixed_percent',
      risk_percentage: 0.02,
      use_grid_trading: false,
      grid_levels: 5,
      grid_range: 0.1
    }
  });

  useEffect(() => {
    fetchBots();
    fetchBrokerCredentials();
  }, []);

  const fetchBots = async () => {
    try {
      const response = await api.get('/bots/');
      setBots(response.data);
    } catch (error) {
      console.error('Erreur lors du chargement des bots', error);
      notifications.show({
        title: 'Erreur',
        message: 'Impossible de charger les bots',
        color: 'red',
      });
    } finally {
      setLoading(false);
    }
  };

  const fetchBrokerCredentials = async () => {
    try {
      const response = await api.get('/broker-credentials/');
      setBrokerCredentials(response.data);
    } catch (error) {
      console.error('Erreur lors du chargement des identifiants broker:', error);
    }
  };

  const getAssetOptions = (broker) => {
    if (broker === 'binance') {
      return [
        { value: 'BTCUSDT', label: 'Bitcoin (BTC/USDT)' },
        { value: 'ETHUSDT', label: 'Ethereum (ETH/USDT)' },
        { value: 'ADAUSDT', label: 'Cardano (ADA/USDT)' },
        { value: 'DOTUSDT', label: 'Polkadot (DOT/USDT)' },
        { value: 'LINKUSDT', label: 'Chainlink (LINK/USDT)' },
        { value: 'BNBUSDT', label: 'Binance Coin (BNB/USDT)' }
      ];
    } else if (broker === 'ig') {
      return [
        { value: 'IX.D.FTSE.DAILY.IP', label: 'FTSE 100' },
        { value: 'IX.D.DAX.DAILY.IP', label: 'DAX 30' },
        { value: 'IX.D.CAC.DAILY.IP', label: 'CAC 40' },
        { value: 'IX.D.SPTRD.DAILY.IP', label: 'S&P 500' },
        { value: 'IX.D.DOW.DAILY.IP', label: 'Dow Jones' },
        { value: 'IX.D.NASDAQ.DAILY.IP', label: 'NASDAQ' },
        { value: 'CS.D.EURUSD.MINI.IP', label: 'EUR/USD' },
        { value: 'CS.D.GBPUSD.MINI.IP', label: 'GBP/USD' },
        { value: 'CS.D.USDJPY.MINI.IP', label: 'USD/JPY' },
        { value: 'CS.D.AUDUSD.MINI.IP', label: 'AUD/USD' },
        { value: 'MT.D.GC.Month2.IP', label: 'Or' },
        { value: 'MT.D.SI.Month1.IP', label: 'Argent' }
      ];
    } else {
      return [
        { value: 'XAU_USD', label: 'Or (XAU/USD)' },
        { value: 'EUR_USD', label: 'EUR/USD' },
        { value: 'GBP_USD', label: 'GBP/USD' },
        { value: 'USD_JPY', label: 'USD/JPY' },
        { value: 'AUD_USD', label: 'AUD/USD' },
        { value: 'USD_CAD', label: 'USD/CAD' }
      ];
    }
  };

  const handleSubmit = async (values) => {
    try {
      const botData = {
        name: values.name,
        asset: values.asset,
        broker: values.broker,
        strategy: values.strategy,
        parameters: {
          rsi_period: values.rsi_period,
          sma_period: values.sma_period,
          tp: values.tp,
          sl: values.sl,
          position_size: values.position_size
        },
        mode: values.mode,
        use_trailing_stop: values.use_trailing_stop,
        trailing_distance: values.trailing_distance,
        use_dynamic_sizing: values.use_dynamic_sizing,
        position_sizing_method: values.position_sizing_method,
        risk_percentage: values.risk_percentage,
        use_grid_trading: values.use_grid_trading,
        grid_levels: values.grid_levels,
        grid_range: values.grid_range
      };

      if (editingBot) {
        await api.put(`/bots/${editingBot.id}/`, botData);
        notifications.show({
          title: 'Bot modifié',
          message: 'Le bot a été modifié avec succès',
          color: 'green',
        });
      } else {
        await api.post('/bots/', botData);
        notifications.show({
          title: 'Bot créé',
          message: 'Le bot a été créé avec succès',
          color: 'green',
        });
      }

      fetchBots();
      setModalOpened(false);
      setEditingBot(null);
      form.reset();
    } catch (error) {
      console.error('Erreur lors de la sauvegarde du bot', error);
      notifications.show({
        title: 'Erreur',
        message: error.response?.data?.error || 'Impossible de sauvegarder le bot',
        color: 'red',
      });
    }
  };

  const handleStartBot = async (botId) => {
    try {
      await api.post(`/bots/${botId}/start/`);
      notifications.show({
        title: 'Bot démarré',
        message: 'Le bot a été démarré avec succès',
        color: 'green',
      });
      fetchBots();
    } catch (error) {
      notifications.show({
        title: 'Erreur',
        message: 'Impossible de démarrer le bot',
        color: 'red',
      });
    }
  };

  const handleStopBot = async (botId) => {
    try {
      await api.post(`/bots/${botId}/stop/`);
      notifications.show({
        title: 'Bot arrêté',
        message: 'Le bot a été arrêté avec succès',
        color: 'orange',
      });
      fetchBots();
    } catch (error) {
      notifications.show({
        title: 'Erreur',
        message: 'Impossible d\'arrêter le bot',
        color: 'red',
      });
    }
  };

  const handleDeleteBot = async (botId) => {
    try {
      await api.delete(`/bots/${botId}/`);
      notifications.show({
        title: 'Bot supprimé',
        message: 'Le bot a été supprimé avec succès',
        color: 'red',
      });
      fetchBots();
    } catch (error) {
      notifications.show({
        title: 'Erreur',
        message: 'Impossible de supprimer le bot',
        color: 'red',
      });
    }
  };

  const openEditModal = (bot) => {
    setEditingBot(bot);
    form.setValues({
      name: bot.name,
      asset: bot.asset,
      broker: bot.broker || 'oanda',
      strategy: bot.strategy,
      rsi_period: bot.parameters?.rsi_period || 14,
      sma_period: bot.parameters?.sma_period || 50,
      tp: bot.parameters?.tp || 0.05,
      sl: bot.parameters?.sl || 0.02,
      position_size: bot.parameters?.position_size || 100,
      mode: bot.mode,
      use_trailing_stop: bot.use_trailing_stop || false,
      trailing_distance: bot.trailing_distance || 0.02,
      use_dynamic_sizing: bot.use_dynamic_sizing || false,
      position_sizing_method: bot.position_sizing_method || 'fixed_percent',
      risk_percentage: bot.risk_percentage || 0.02,
      use_grid_trading: bot.use_grid_trading || false,
      grid_levels: bot.grid_levels || 5,
      grid_range: bot.grid_range || 0.1
    });
    setModalOpened(true);
  };

  const openCreateModal = () => {
    setEditingBot(null);
    form.reset();
    setModalOpened(true);
  };

  if (loading) {
    return (
      <Center h={400}>
        <Loader size="lg" />
      </Center>
    );
  }

  return (
    <Stack gap="lg">
      <Group justify="space-between">
        <div>
          <Title order={1}>Mes Bots de Trading</Title>
          <Text c="dimmed">
            Gérez vos bots de trading automatisés
          </Text>
        </div>
        <Button
          leftIcon={<IconPlus size={16} />}
          onClick={openCreateModal}
        >
          Nouveau Bot
        </Button>
      </Group>

      {bots.length === 0 ? (
        <Alert
          icon={<IconRobot size={16} />}
          title="Aucun bot configuré"
          color="blue"
          variant="light"
        >
          Créez votre premier bot de trading pour commencer à automatiser vos stratégies.
        </Alert>
      ) : (
        <Card withBorder>
          <Table>
            <Table.Thead>
              <Table.Tr>
                <Table.Th>Nom</Table.Th>
                <Table.Th>Broker</Table.Th>
                <Table.Th>Asset</Table.Th>
                <Table.Th>Stratégie</Table.Th>
                <Table.Th>Mode</Table.Th>
                <Table.Th>Statut</Table.Th>
                <Table.Th>Actions</Table.Th>
              </Table.Tr>
            </Table.Thead>
            <Table.Tbody>
              {bots.map((bot) => (
                <Table.Tr key={bot.id}>
                  <Table.Td>
                    <Text fw={500}>{bot.name}</Text>
                  </Table.Td>
                  <Table.Td>
                    <Badge
                      color={
                        bot.broker === 'binance' ? 'yellow' : 
                        bot.broker === 'ig' ? 'green' : 'blue'
                      }
                      variant="light"
                    >
                      {bot.broker?.toUpperCase() || 'OANDA'}
                    </Badge>
                  </Table.Td>
                  <Table.Td>{bot.asset}</Table.Td>
                  <Table.Td>{bot.strategy}</Table.Td>
                  <Table.Td>
                    <Badge
                      color={bot.mode === 'live' ? 'red' : 'blue'}
                      variant="light"
                    >
                      {bot.mode === 'live' ? 'Live' : 'Paper'}
                    </Badge>
                  </Table.Td>
                  <Table.Td>
                    <Badge
                      color={bot.status === 'running' ? 'green' : 'gray'}
                      variant="light"
                    >
                      {bot.status === 'running' ? 'Actif' : 'Arrêté'}
                    </Badge>
                  </Table.Td>
                  <Table.Td>
                    <Group gap="xs">
                      {bot.status === 'stopped' ? (
                        <ActionIcon
                          color="green"
                          variant="light"
                          onClick={() => handleStartBot(bot.id)}
                        >
                          <IconPlayerPlay size={16} />
                        </ActionIcon>
                      ) : (
                        <ActionIcon
                          color="orange"
                          variant="light"
                          onClick={() => handleStopBot(bot.id)}
                        >
                          <IconPlayerStop size={16} />
                        </ActionIcon>
                      )}
                      <ActionIcon
                        color="blue"
                        variant="light"
                        onClick={() => openEditModal(bot)}
                      >
                        <IconSettings size={16} />
                      </ActionIcon>
                      <ActionIcon
                        color="red"
                        variant="light"
                        onClick={() => handleDeleteBot(bot.id)}
                      >
                        <IconTrash size={16} />
                      </ActionIcon>
                    </Group>
                  </Table.Td>
                </Table.Tr>
              ))}
            </Table.Tbody>
          </Table>
        </Card>
      )}

      <Modal
        opened={modalOpened}
        onClose={() => {
          setModalOpened(false);
          setEditingBot(null);
          form.reset();
        }}
        title={editingBot ? 'Modifier le Bot' : 'Créer un Nouveau Bot'}
        size="lg"
      >
        <form onSubmit={form.onSubmit(handleSubmit)}>
          <Stack gap="md">
            <TextInput
              label="Nom du bot"
              placeholder="Mon bot de trading"
              required
              {...form.getInputProps('name')}
            />

            <Grid>
              <Grid.Col span={6}>
                <Select
                  label="Broker"
                  placeholder="Sélectionnez un broker"
                  data={[
                    { value: 'binance', label: 'Binance', disabled: !brokerCredentials.some(c => c.broker === 'binance' && c.is_active) },
                    { value: 'oanda', label: 'Oanda', disabled: !brokerCredentials.some(c => c.broker === 'oanda' && c.is_active) },
                    { value: 'ig', label: 'IG', disabled: !brokerCredentials.some(c => c.broker === 'ig' && c.is_active) }
                  ]}
                  {...form.getInputProps('broker')}
                  onChange={(value) => {
                    form.setFieldValue('broker', value);
                    // Reset asset when broker changes
                    const defaultAsset = value === 'binance' ? 'BTCUSDT' : 
                                        value === 'ig' ? 'IX.D.FTSE.DAILY.IP' : 'XAU_USD';
                    form.setFieldValue('asset', defaultAsset);
                  }}
                />
              </Grid.Col>
              <Grid.Col span={6}>
                <Select
                  label="Asset"
                  data={getAssetOptions(form.values.broker)}
                  {...form.getInputProps('asset')}
                />
              </Grid.Col>
            </Grid>

            <Grid>
              <Grid.Col span={6}>
                <Select
                  label="Stratégie"
                  data={[
                    { value: 'RSI_SMA', label: 'RSI + SMA' },
                    { value: 'MACD', label: 'MACD' },
                    { value: 'EMA_CROSS', label: 'EMA Cross' }
                  ]}
                  {...form.getInputProps('strategy')}
                />
              </Grid.Col>
            </Grid>

            <Grid>
              <Grid.Col span={6}>
                <NumberInput
                  label="Période RSI"
                  min={5}
                  max={50}
                  {...form.getInputProps('rsi_period')}
                />
              </Grid.Col>
              <Grid.Col span={6}>
                <NumberInput
                  label="Période SMA"
                  min={10}
                  max={200}
                  {...form.getInputProps('sma_period')}
                />
              </Grid.Col>
            </Grid>

            <Grid>
              <Grid.Col span={4}>
                <NumberInput
                  label="Take Profit"
                  step={0.01}
                  min={0.01}
                  max={1}
                  {...form.getInputProps('tp')}
                />
              </Grid.Col>
              <Grid.Col span={4}>
                <NumberInput
                  label="Stop Loss"
                  step={0.01}
                  min={0.01}
                  max={1}
                  {...form.getInputProps('sl')}
                />
              </Grid.Col>
              <Grid.Col span={4}>
                <NumberInput
                  label="Taille Position"
                  min={1}
                  max={10000}
                  {...form.getInputProps('position_size')}
                />
              </Grid.Col>
            </Grid>

            <Select
              label="Mode de trading"
              data={[
                { value: 'paper', label: 'Paper Trading (Simulation)' },
                { value: 'live', label: 'Live Trading (Réel)' }
              ]}
              {...form.getInputProps('mode')}
            />

            <div>
              <Text size="md" fw={500} mb="sm">Fonctionnalités Avancées</Text>
              
              <Stack gap="sm">
                {/* Trailing Stop */}
                <Card withBorder p="sm">
                  <Stack gap="xs">
                    <Group justify="space-between">
                      <Text size="sm" fw={500}>Trailing Stop</Text>
                      <Switch
                        {...form.getInputProps('use_trailing_stop', { type: 'checkbox' })}
                      />
                    </Group>
                    {form.values.use_trailing_stop && (
                      <NumberInput
                        label="Distance de trailing (%)"
                        step={0.01}
                        min={0.01}
                        max={0.1}
                        size="xs"
                        {...form.getInputProps('trailing_distance')}
                      />
                    )}
                  </Stack>
                </Card>

                {/* Position Sizing Dynamique */}
                <Card withBorder p="sm">
                  <Stack gap="xs">
                    <Group justify="space-between">
                      <Text size="sm" fw={500}>Position Sizing Dynamique</Text>
                      <Switch
                        {...form.getInputProps('use_dynamic_sizing', { type: 'checkbox' })}
                      />
                    </Group>
                    {form.values.use_dynamic_sizing && (
                      <Grid>
                        <Grid.Col span={6}>
                          <Select
                            label="Méthode"
                            size="xs"
                            data={[
                              { value: 'fixed_percent', label: 'Pourcentage fixe' },
                              { value: 'volatility_based', label: 'Basé sur volatilité' },
                              { value: 'kelly', label: 'Critère de Kelly' }
                            ]}
                            {...form.getInputProps('position_sizing_method')}
                          />
                        </Grid.Col>
                        <Grid.Col span={6}>
                          <NumberInput
                            label="Risque (%)"
                            step={0.01}
                            min={0.01}
                            max={0.1}
                            size="xs"
                            {...form.getInputProps('risk_percentage')}
                          />
                        </Grid.Col>
                      </Grid>
                    )}
                  </Stack>
                </Card>

                {/* Grid Trading */}
                <Card withBorder p="sm">
                  <Stack gap="xs">
                    <Group justify="space-between">
                      <Text size="sm" fw={500}>Grid Trading</Text>
                      <Switch
                        {...form.getInputProps('use_grid_trading', { type: 'checkbox' })}
                      />
                    </Group>
                    {form.values.use_grid_trading && (
                      <Grid>
                        <Grid.Col span={6}>
                          <NumberInput
                            label="Niveaux"
                            min={3}
                            max={20}
                            size="xs"
                            {...form.getInputProps('grid_levels')}
                          />
                        </Grid.Col>
                        <Grid.Col span={6}>
                          <NumberInput
                            label="Fourchette (%)"
                            step={0.01}
                            min={0.01}
                            max={0.5}
                            size="xs"
                            {...form.getInputProps('grid_range')}
                          />
                        </Grid.Col>
                      </Grid>
                    )}
                  </Stack>
                </Card>
              </Stack>
            </div>

            {brokerCredentials.length === 0 && (
              <Alert color="orange" icon={<IconAlertCircle size={16} />}>
                <Text size="sm">
                  Aucun identifiant broker configuré. Veuillez d'abord ajouter vos identifiants dans la page de compte.
                </Text>
              </Alert>
            )}

            {!brokerCredentials.some(c => c.broker === form.values.broker && c.is_active) && form.values.broker && (
              <Alert color="red" icon={<IconAlertCircle size={16} />}>
                <Text size="sm">
                  Aucun identifiant actif pour {form.values.broker.toUpperCase()}. Veuillez configurer vos identifiants dans la page de compte.
                </Text>
              </Alert>
            )}

            <Group justify="flex-end" mt="md">
              <Button
                variant="light"
                onClick={() => {
                  setModalOpened(false);
                  setEditingBot(null);
                  form.reset();
                }}
              >
                Annuler
              </Button>
              <Button type="submit">
                {editingBot ? 'Modifier' : 'Créer'}
              </Button>
            </Group>
          </Stack>
        </form>
      </Modal>
    </Stack>
  );
}

export default BotsPage;
