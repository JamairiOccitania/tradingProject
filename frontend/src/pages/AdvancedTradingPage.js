import React, { useState, useEffect } from 'react';
import {
  Stack,
  Title,
  Text,
  Tabs,
  Card,
  Grid,
  Badge,
  Group,
  Button,
  Modal,
  TextInput,
  NumberInput,
  Select,
  Switch,
  Table,
  ActionIcon,
  Alert,
  Loader,
  Center
} from '@mantine/core';
import {
  IconTrendingUp,
  IconScale,
  IconShield,
  IconGrid3x3,
  IconArrowsExchange,
  IconPlus,
  IconPlayerPlay,
  IconPlayerStop,
  IconSettings,
  IconTrash,
  IconAlertCircle
} from '@tabler/icons-react';
import { useForm } from '@mantine/form';
import { notifications } from '@mantine/notifications';
import api from '../services/api';

function AdvancedTradingPage() {
  const [activeTab, setActiveTab] = useState('trailing-stops');
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState({});
  
  // States pour chaque fonctionnalité
  const [trailingStops, setTrailingStops] = useState([]);
  const [positionSizing, setPositionSizing] = useState([]);
  const [hedgingStrategies, setHedgingStrategies] = useState([]);
  const [gridBots, setGridBots] = useState([]);
  const [arbitrageStrategies, setArbitrageStrategies] = useState([]);
  
  // Modals
  const [trailingStopModal, setTrailingStopModal] = useState(false);
  const [positionSizingModal, setPositionSizingModal] = useState(false);
  const [hedgingModal, setHedgingModal] = useState(false);
  const [gridBotModal, setGridBotModal] = useState(false);
  const [arbitrageModal, setArbitrageModal] = useState(false);

  // Forms
  const trailingStopForm = useForm({
    initialValues: {
      asset: 'XAU_USD',
      position_type: 'long',
      entry_price: 2000,
      trailing_distance: 0.02,
      stop_price: 1960
    }
  });

  const positionSizingForm = useForm({
    initialValues: {
      name: '',
      method: 'fixed_percent',
      risk_percentage: 0.02,
      max_position_size: 10000,
      min_position_size: 100
    }
  });

  const hedgingForm = useForm({
    initialValues: {
      name: '',
      primary_asset: 'XAU_USD',
      hedge_asset: 'DXY',
      correlation_coefficient: -0.8,
      hedge_ratio: 0.8,
      primary_position_size: 1000,
      hedge_position_size: 800,
      primary_position_type: 'long',
      hedge_position_type: 'short'
    }
  });

  const gridBotForm = useForm({
    initialValues: {
      name: '',
      asset: 'XAU_USD',
      lower_price: 1900,
      upper_price: 2100,
      grid_levels: 10,
      order_size: 100,
      total_investment: 10000,
      profit_per_grid: 0.01
    }
  });

  const arbitrageForm = useForm({
    initialValues: {
      name: '',
      asset_a: 'XAU_USD',
      asset_b: 'XAG_USD',
      expected_ratio: 80,
      threshold_percentage: 2,
      position_size: 1000,
      profit_target: 0.05,
      max_loss: 0.02
    }
  });

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [statsRes, trailingRes, positionRes, hedgingRes, gridRes, arbitrageRes] = await Promise.all([
        api.get('/advanced-stats/'),
        api.get('/trailing-stops/'),
        api.get('/position-sizing/'),
        api.get('/hedging/'),
        api.get('/grid-bots/'),
        api.get('/arbitrage/')
      ]);

      setStats(statsRes.data);
      setTrailingStops(trailingRes.data);
      setPositionSizing(positionRes.data);
      setHedgingStrategies(hedgingRes.data);
      setGridBots(gridRes.data);
      setArbitrageStrategies(arbitrageRes.data);
    } catch (error) {
      console.error('Erreur lors du chargement des données', error);
      notifications.show({
        title: 'Erreur',
        message: 'Impossible de charger les données',
        color: 'red',
      });
    } finally {
      setLoading(false);
    }
  };

  const handleTrailingStopSubmit = async (values) => {
    try {
      await api.post('/trailing-stops/', {
        ...values,
        current_price: values.entry_price
      });
      notifications.show({
        title: 'Trailing Stop créé',
        message: 'Le trailing stop a été créé avec succès',
        color: 'green',
      });
      setTrailingStopModal(false);
      fetchData();
    } catch (error) {
      notifications.show({
        title: 'Erreur',
        message: 'Impossible de créer le trailing stop',
        color: 'red',
      });
    }
  };

  const handlePositionSizingSubmit = async (values) => {
    try {
      await api.post('/position-sizing/', values);
      notifications.show({
        title: 'Configuration créée',
        message: 'La configuration de position sizing a été créée',
        color: 'green',
      });
      setPositionSizingModal(false);
      fetchData();
    } catch (error) {
      notifications.show({
        title: 'Erreur',
        message: 'Impossible de créer la configuration',
        color: 'red',
      });
    }
  };

  const handleHedgingSubmit = async (values) => {
    try {
      await api.post('/hedging/', values);
      notifications.show({
        title: 'Stratégie de hedging créée',
        message: 'La stratégie a été créée avec succès',
        color: 'green',
      });
      setHedgingModal(false);
      fetchData();
    } catch (error) {
      notifications.show({
        title: 'Erreur',
        message: 'Impossible de créer la stratégie',
        color: 'red',
      });
    }
  };

  const handleGridBotSubmit = async (values) => {
    try {
      await api.post('/grid-bots/', values);
      notifications.show({
        title: 'Grid Bot créé',
        message: 'Le grid bot a été créé avec succès',
        color: 'green',
      });
      setGridBotModal(false);
      fetchData();
    } catch (error) {
      notifications.show({
        title: 'Erreur',
        message: 'Impossible de créer le grid bot',
        color: 'red',
      });
    }
  };

  const handleArbitrageSubmit = async (values) => {
    try {
      await api.post('/arbitrage/', values);
      notifications.show({
        title: 'Stratégie d\'arbitrage créée',
        message: 'La stratégie a été créée avec succès',
        color: 'green',
      });
      setArbitrageModal(false);
      fetchData();
    } catch (error) {
      notifications.show({
        title: 'Erreur',
        message: 'Impossible de créer la stratégie',
        color: 'red',
      });
    }
  };

  const startGridBot = async (id) => {
    try {
      await api.post(`/grid-bots/${id}/start/`);
      notifications.show({
        title: 'Grid Bot démarré',
        message: 'Le grid bot a été démarré',
        color: 'green',
      });
      fetchData();
    } catch (error) {
      notifications.show({
        title: 'Erreur',
        message: 'Impossible de démarrer le grid bot',
        color: 'red',
      });
    }
  };

  const stopGridBot = async (id) => {
    try {
      await api.post(`/grid-bots/${id}/stop/`);
      notifications.show({
        title: 'Grid Bot arrêté',
        message: 'Le grid bot a été arrêté',
        color: 'orange',
      });
      fetchData();
    } catch (error) {
      notifications.show({
        title: 'Erreur',
        message: 'Impossible d\'arrêter le grid bot',
        color: 'red',
      });
    }
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
      <div>
        <Title order={1}>Trading Avancé</Title>
        <Text c="dimmed">
          Fonctionnalités avancées pour optimiser vos stratégies de trading
        </Text>
      </div>

      {/* Statistiques globales */}
      <Grid>
        <Grid.Col span={2.4}>
          <Card withBorder>
            <Group justify="space-between">
              <div>
                <Text size="sm" c="dimmed">Trailing Stops</Text>
                <Text fw={700} size="xl">{stats.trailing_stops?.active || 0}</Text>
              </div>
              <IconTrendingUp size={24} color="blue" />
            </Group>
          </Card>
        </Grid.Col>
        <Grid.Col span={2.4}>
          <Card withBorder>
            <Group justify="space-between">
              <div>
                <Text size="sm" c="dimmed">Position Sizing</Text>
                <Text fw={700} size="xl">{stats.position_sizing?.active_configs || 0}</Text>
              </div>
              <IconScale size={24} color="green" />
            </Group>
          </Card>
        </Grid.Col>
        <Grid.Col span={2.4}>
          <Card withBorder>
            <Group justify="space-between">
              <div>
                <Text size="sm" c="dimmed">Hedging</Text>
                <Text fw={700} size="xl">{stats.hedging?.active_strategies || 0}</Text>
              </div>
              <IconShield size={24} color="orange" />
            </Group>
          </Card>
        </Grid.Col>
        <Grid.Col span={2.4}>
          <Card withBorder>
            <Group justify="space-between">
              <div>
                <Text size="sm" c="dimmed">Grid Bots</Text>
                <Text fw={700} size="xl">{stats.grid_bots?.running || 0}</Text>
              </div>
              <IconGrid3x3 size={24} color="purple" />
            </Group>
          </Card>
        </Grid.Col>
        <Grid.Col span={2.4}>
          <Card withBorder>
            <Group justify="space-between">
              <div>
                <Text size="sm" c="dimmed">Arbitrage</Text>
                <Text fw={700} size="xl">{stats.arbitrage?.monitoring || 0}</Text>
              </div>
              <IconArrowsExchange size={24} color="red" />
            </Group>
          </Card>
        </Grid.Col>
      </Grid>

      <Tabs value={activeTab} onChange={setActiveTab}>
        <Tabs.List>
          <Tabs.Tab value="trailing-stops" leftSection={<IconTrendingUp size={16} />}>
            Trailing Stops
          </Tabs.Tab>
          <Tabs.Tab value="position-sizing" leftSection={<IconScale size={16} />}>
            Position Sizing
          </Tabs.Tab>
          <Tabs.Tab value="hedging" leftSection={<IconShield size={16} />}>
            Hedging
          </Tabs.Tab>
          <Tabs.Tab value="grid-bots" leftSection={<IconGrid3x3 size={16} />}>
            Grid Bots
          </Tabs.Tab>
          <Tabs.Tab value="arbitrage" leftSection={<IconArrowsExchange size={16} />}>
            Arbitrage
          </Tabs.Tab>
        </Tabs.List>

        {/* Trailing Stops Tab */}
        <Tabs.Panel value="trailing-stops">
          <Stack gap="md">
            <Group justify="space-between">
              <Text size="lg" fw={500}>Trailing Stops Actifs</Text>
              <Button 
                leftSection={<IconPlus size={16} />}
                onClick={() => setTrailingStopModal(true)}
              >
                Nouveau Trailing Stop
              </Button>
            </Group>
            
            {trailingStops.length === 0 ? (
              <Alert icon={<IconAlertCircle size={16} />} color="blue" variant="light">
                Aucun trailing stop configuré
              </Alert>
            ) : (
              <Card withBorder>
                <Table>
                  <Table.Thead>
                    <Table.Tr>
                      <Table.Th>Asset</Table.Th>
                      <Table.Th>Type</Table.Th>
                      <Table.Th>Prix d'entrée</Table.Th>
                      <Table.Th>Prix actuel</Table.Th>
                      <Table.Th>Stop Price</Table.Th>
                      <Table.Th>Distance</Table.Th>
                      <Table.Th>Statut</Table.Th>
                    </Table.Tr>
                  </Table.Thead>
                  <Table.Tbody>
                    {trailingStops.map((stop) => (
                      <Table.Tr key={stop.id}>
                        <Table.Td>{stop.asset}</Table.Td>
                        <Table.Td>
                          <Badge color={stop.position_type === 'long' ? 'green' : 'red'}>
                            {stop.position_type}
                          </Badge>
                        </Table.Td>
                        <Table.Td>{stop.entry_price}</Table.Td>
                        <Table.Td>{stop.current_price}</Table.Td>
                        <Table.Td>{stop.stop_price}</Table.Td>
                        <Table.Td>{(stop.trailing_distance * 100).toFixed(1)}%</Table.Td>
                        <Table.Td>
                          <Badge color={stop.status === 'active' ? 'green' : 'gray'}>
                            {stop.status}
                          </Badge>
                        </Table.Td>
                      </Table.Tr>
                    ))}
                  </Table.Tbody>
                </Table>
              </Card>
            )}
          </Stack>
        </Tabs.Panel>

        {/* Grid Bots Tab */}
        <Tabs.Panel value="grid-bots">
          <Stack gap="md">
            <Group justify="space-between">
              <Text size="lg" fw={500}>Grid Bots</Text>
              <Button 
                leftSection={<IconPlus size={16} />}
                onClick={() => setGridBotModal(true)}
              >
                Nouveau Grid Bot
              </Button>
            </Group>
            
            {gridBots.length === 0 ? (
              <Alert icon={<IconAlertCircle size={16} />} color="blue" variant="light">
                Aucun grid bot configuré
              </Alert>
            ) : (
              <Card withBorder>
                <Table>
                  <Table.Thead>
                    <Table.Tr>
                      <Table.Th>Nom</Table.Th>
                      <Table.Th>Asset</Table.Th>
                      <Table.Th>Fourchette</Table.Th>
                      <Table.Th>Niveaux</Table.Th>
                      <Table.Th>Profit Total</Table.Th>
                      <Table.Th>Statut</Table.Th>
                      <Table.Th>Actions</Table.Th>
                    </Table.Tr>
                  </Table.Thead>
                  <Table.Tbody>
                    {gridBots.map((bot) => (
                      <Table.Tr key={bot.id}>
                        <Table.Td>{bot.name}</Table.Td>
                        <Table.Td>{bot.asset}</Table.Td>
                        <Table.Td>{bot.lower_price} - {bot.upper_price}</Table.Td>
                        <Table.Td>{bot.grid_levels}</Table.Td>
                        <Table.Td>{bot.total_profit.toFixed(2)}$</Table.Td>
                        <Table.Td>
                          <Badge color={bot.status === 'running' ? 'green' : 'gray'}>
                            {bot.status}
                          </Badge>
                        </Table.Td>
                        <Table.Td>
                          <Group gap="xs">
                            {bot.status === 'stopped' ? (
                              <ActionIcon
                                color="green"
                                variant="light"
                                onClick={() => startGridBot(bot.id)}
                              >
                                <IconPlayerPlay size={16} />
                              </ActionIcon>
                            ) : (
                              <ActionIcon
                                color="orange"
                                variant="light"
                                onClick={() => stopGridBot(bot.id)}
                              >
                                <IconPlayerStop size={16} />
                              </ActionIcon>
                            )}
                          </Group>
                        </Table.Td>
                      </Table.Tr>
                    ))}
                  </Table.Tbody>
                </Table>
              </Card>
            )}
          </Stack>
        </Tabs.Panel>

        {/* Autres onglets similaires... */}
      </Tabs>

      {/* Modals */}
      <Modal
        opened={trailingStopModal}
        onClose={() => setTrailingStopModal(false)}
        title="Nouveau Trailing Stop"
        size="md"
      >
        <form onSubmit={trailingStopForm.onSubmit(handleTrailingStopSubmit)}>
          <Stack gap="md">
            <Select
              label="Asset"
              data={[
                { value: 'XAU_USD', label: 'Or (XAU/USD)' },
                { value: 'EUR_USD', label: 'EUR/USD' },
                { value: 'GBP_USD', label: 'GBP/USD' },
                { value: 'USD_JPY', label: 'USD/JPY' }
              ]}
              {...trailingStopForm.getInputProps('asset')}
            />
            <Select
              label="Type de position"
              data={[
                { value: 'long', label: 'Long' },
                { value: 'short', label: 'Short' }
              ]}
              {...trailingStopForm.getInputProps('position_type')}
            />
            <NumberInput
              label="Prix d'entrée"
              {...trailingStopForm.getInputProps('entry_price')}
            />
            <NumberInput
              label="Distance de trailing (%)"
              step={0.01}
              min={0.01}
              max={0.1}
              {...trailingStopForm.getInputProps('trailing_distance')}
            />
            <NumberInput
              label="Prix de stop initial"
              {...trailingStopForm.getInputProps('stop_price')}
            />
            <Group justify="flex-end">
              <Button variant="light" onClick={() => setTrailingStopModal(false)}>
                Annuler
              </Button>
              <Button type="submit">Créer</Button>
            </Group>
          </Stack>
        </form>
      </Modal>

      <Modal
        opened={gridBotModal}
        onClose={() => setGridBotModal(false)}
        title="Nouveau Grid Bot"
        size="lg"
      >
        <form onSubmit={gridBotForm.onSubmit(handleGridBotSubmit)}>
          <Stack gap="md">
            <TextInput
              label="Nom du Grid Bot"
              {...gridBotForm.getInputProps('name')}
            />
            <Select
              label="Asset"
              data={[
                { value: 'XAU_USD', label: 'Or (XAU/USD)' },
                { value: 'EUR_USD', label: 'EUR/USD' },
                { value: 'BTC_USD', label: 'Bitcoin' }
              ]}
              {...gridBotForm.getInputProps('asset')}
            />
            <Grid>
              <Grid.Col span={6}>
                <NumberInput
                  label="Prix plancher"
                  {...gridBotForm.getInputProps('lower_price')}
                />
              </Grid.Col>
              <Grid.Col span={6}>
                <NumberInput
                  label="Prix plafond"
                  {...gridBotForm.getInputProps('upper_price')}
                />
              </Grid.Col>
            </Grid>
            <Grid>
              <Grid.Col span={6}>
                <NumberInput
                  label="Nombre de niveaux"
                  min={3}
                  max={50}
                  {...gridBotForm.getInputProps('grid_levels')}
                />
              </Grid.Col>
              <Grid.Col span={6}>
                <NumberInput
                  label="Taille par ordre"
                  {...gridBotForm.getInputProps('order_size')}
                />
              </Grid.Col>
            </Grid>
            <NumberInput
              label="Investissement total"
              {...gridBotForm.getInputProps('total_investment')}
            />
            <NumberInput
              label="Profit par niveau (%)"
              step={0.001}
              min={0.001}
              max={0.1}
              {...gridBotForm.getInputProps('profit_per_grid')}
            />
            <Group justify="flex-end">
              <Button variant="light" onClick={() => setGridBotModal(false)}>
                Annuler
              </Button>
              <Button type="submit">Créer</Button>
            </Group>
          </Stack>
        </form>
      </Modal>
    </Stack>
  );
}

export default AdvancedTradingPage;
