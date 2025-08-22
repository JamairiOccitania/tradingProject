import React, { useState, useEffect } from 'react';
import {
  Stack,
  Title,
  Text,
  Card,
  Button,
  Group,
  Grid,
  Select,
  TextInput,
  Textarea,
  Table,
  Badge,
  Alert,
  Loader,
  Center,
  Modal,
  NumberInput,
  Progress
} from '@mantine/core';
import {
  IconChartLine,
  IconPlay,
  IconHistory,
  IconTrendingUp,
  IconTrendingDown,
  IconAlertCircle,
  IconCalendar,
  IconSettings
} from '@tabler/icons-react';
import { useForm } from '@mantine/form';
import { notifications } from '@mantine/notifications';
import api from '../services/api';

const BacktestingPage = () => {
  const [backtests, setBacktests] = useState([]);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [modalOpened, setModalOpened] = useState(false);
  const [selectedBacktest, setSelectedBacktest] = useState(null);

  const form = useForm({
    initialValues: {
      asset: 'XAU_USD',
      strategy: 'RSI_SMA',
      start_date: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000), // 30 jours avant
      end_date: new Date(),
      rsi_period: 14,
      sma_period: 50,
      tp: 0.05,
      sl: 0.02,
      position_size: 100
    },
    validate: {
      start_date: (value) => !value ? 'Date de début requise' : null,
      end_date: (value, values) => {
        if (!value) return 'Date de fin requise';
        if (value <= values.start_date) return 'La date de fin doit être après la date de début';
        return null;
      }
    }
  });

  useEffect(() => {
    fetchBacktests();
  }, []);

  useEffect(() => {
    console.log(backtests);
  }, backtests);

  const fetchBacktests = async () => {
    try {
      const response = await api.get('/backtests/');
      console.log(response.data)
      setBacktests(response.data);
    } catch (error) {
      console.error('Erreur lors du chargement des backtests', error);
      notifications.show({
        title: 'Erreur',
        message: 'Impossible de charger l\'historique des backtests',
        color: 'red',
      });
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (values) => {
    setSubmitting(true);
    try {
      const backtestData = {
        asset: values.asset,
        strategy: values.strategy,
        start_date: values.start_date.toISOString(),
        end_date: values.end_date.toISOString(),
        parameters: {
          rsi_period: values.rsi_period,
          sma_period: values.sma_period,
          tp: values.tp,
          sl: values.sl,
          position_size: values.position_size
        }
      };

      await api.post('/backtests/', backtestData);
      notifications.show({
        title: 'Backtest lancé',
        message: 'Le backtest a été lancé avec succès',
        color: 'green',
      });

      fetchBacktests();
      setModalOpened(false);
      form.reset();
    } catch (error) {
      console.error('Erreur lors du lancement du backtest', error);
      notifications.show({
        title: 'Erreur',
        message: 'Impossible de lancer le backtest',
        color: 'red',
      });
    } finally {
      setSubmitting(false);
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'completed': return 'green';
      case 'running': return 'blue';
      case 'failed': return 'red';
      default: return 'gray';
    }
  };

  const getStatusLabel = (status) => {
    switch (status) {
      case 'completed': return 'Terminé';
      case 'running': return 'En cours';
      case 'failed': return 'Échoué';
      case 'pending': return 'En attente';
      default: return status;
    }
  };

  const ResultsCard = ({ results }) => {
    if (!results) return <Text c="dimmed">Aucun résultat</Text>;
    if (results.error) return <Text c="red">{results.error}</Text>;

    const isProfit = results.profit_loss > 0;

    return (
      <Grid>
        <Grid.Col span={6}>
          <Stack gap="xs">
            <Group gap="xs">
              {isProfit ? (
                <IconTrendingUp size={16} color="green" />
              ) : (
                <IconTrendingDown size={16} color="red" />
              )}
              <Text fw={500}>P&L Total</Text>
            </Group>
            <Text size="xl" fw={700} c={isProfit ? 'green' : 'red'}>
              {isProfit ? '+' : ''}{results.profit_loss}€
            </Text>
          </Stack>
        </Grid.Col>
        <Grid.Col span={6}>
          <Stack gap="xs">
            <Text fw={500}>Taux de réussite</Text>
            <Text size="xl" fw={700}>
              {results.win_rate}%
            </Text>
            <Progress value={results.win_rate} color={results.win_rate > 50 ? 'green' : 'red'} />
          </Stack>
        </Grid.Col>
        <Grid.Col span={6}>
          <Stack gap="xs">
            <Text fw={500}>Nombre de trades</Text>
            <Text size="lg">{results.total_trades}</Text>
          </Stack>
        </Grid.Col>
        <Grid.Col span={6}>
          <Stack gap="xs">
            <Text fw={500}>Balance finale</Text>
            <Text size="lg" fw={500}>{results.final_balance}€</Text>
          </Stack>
        </Grid.Col>
      </Grid>
    );
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
          <Title order={1}>Backtesting</Title>
          <Text c="dimmed">
            Testez vos stratégies sur des données historiques
          </Text>
        </div>
        <Button
          leftIcon={<IconPlay size={16} />}
          onClick={() => setModalOpened(true)}
        >
          Nouveau Backtest
        </Button>
      </Group>

      {backtests.length === 0 ? (
        <Alert
          icon={<IconChartLine size={16} />}
          title="Aucun backtest"
          color="blue"
          variant="light"
        >
          Lancez votre premier backtest pour analyser les performances de vos stratégies.
        </Alert>
      ) : (
        <Card withBorder>
          <Table>
            <Table.Thead>
              <Table.Tr>
                <Table.Th>Asset</Table.Th>
                <Table.Th>Stratégie</Table.Th>
                <Table.Th>Période</Table.Th>
                <Table.Th>Statut</Table.Th>
                <Table.Th>P&L</Table.Th>
                <Table.Th>Actions</Table.Th>
              </Table.Tr>
            </Table.Thead>
            <Table.Tbody>
              {backtests.map((backtest) => (
                <Table.Tr key={backtest.id}>
                  <Table.Td>
                    <Text fw={500}>{backtest.asset}</Text>
                  </Table.Td>
                  <Table.Td>{backtest.strategy}</Table.Td>
                  <Table.Td>
                    <Text size="sm">
                      {new Date(backtest.start_date).toLocaleDateString('fr-FR')} - {' '}
                      {new Date(backtest.end_date).toLocaleDateString('fr-FR')}
                    </Text>
                  </Table.Td>
                  <Table.Td>
                    <Badge
                      color={getStatusColor(backtest.status)}
                      variant="light"
                    >
                      {getStatusLabel(backtest.status)}
                    </Badge>
                  </Table.Td>
                  <Table.Td>
                    {backtest.results?.profit_loss ? (
                      <Text
                        fw={500}
                        c={backtest.results.profit_loss > 0 ? 'green' : 'red'}
                      >
                        {backtest.results.profit_loss > 0 ? '+' : ''}
                        {backtest.results.profit_loss}€
                      </Text>
                    ) : (
                      <Text c="dimmed">-</Text>
                    )}
                  </Table.Td>
                  <Table.Td>
                    <Button
                      size="xs"
                      variant="light"
                      onClick={() => setSelectedBacktest(backtest)}
                      disabled={!backtest.results}
                    >
                      Détails
                    </Button>
                  </Table.Td>
                </Table.Tr>
              ))}
            </Table.Tbody>
          </Table>
        </Card>
      )}

      {/* Modal de création */}
      <Modal
        opened={modalOpened}
        onClose={() => {
          setModalOpened(false);
          form.reset();
        }}
        title="Nouveau Backtest"
        size="lg"
      >
        <form onSubmit={form.onSubmit(handleSubmit)}>
          <Stack gap="md">
            <Grid>
              <Grid.Col span={6}>
                <Select
                  label="Asset"
                  data={[
                    { value: 'XAU_USD', label: 'Or (XAU/USD)' },
                    { value: 'EUR_USD', label: 'EUR/USD' },
                    { value: 'GBP_USD', label: 'GBP/USD' },
                    { value: 'USD_JPY', label: 'USD/JPY' }
                  ]}
                  {...form.getInputProps('asset')}
                />
              </Grid.Col>
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
                <TextInput
                  label="Date de début"
                  placeholder="Sélectionner une date"
                  leftIcon={<IconCalendar size={16} />}
                  {...form.getInputProps('start_date')}
                />
              </Grid.Col>
              <Grid.Col span={6}>
                <TextInput
                  label="Date de fin"
                  placeholder="Sélectionner une date"
                  leftIcon={<IconCalendar size={16} />}
                  {...form.getInputProps('end_date')}
                />
              </Grid.Col>
            </Grid>

            <Text fw={500} size="sm" mt="md">Paramètres de la stratégie</Text>
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

            <Group justify="flex-end" mt="md">
              <Button
                variant="light"
                onClick={() => {
                  setModalOpened(false);
                  form.reset();
                }}
              >
                Annuler
              </Button>
              <Button
                type="submit"
                loading={submitting}
                leftIcon={<IconPlay size={16} />}
              >
                Lancer le Backtest
              </Button>
            </Group>
          </Stack>
        </form>
      </Modal>

      {/* Modal de détails */}
      <Modal
        opened={!!selectedBacktest}
        onClose={() => setSelectedBacktest(null)}
        title={`Résultats - ${selectedBacktest?.asset} (${selectedBacktest?.strategy})`}
        size="lg"
      >
        {selectedBacktest && (
          <Stack gap="md">
            <Group>
              <IconHistory size={16} />
              <Text size="sm" c="dimmed">
                {new Date(selectedBacktest.start_date).toLocaleDateString('fr-FR')} - {' '}
                {new Date(selectedBacktest.end_date).toLocaleDateString('fr-FR')}
              </Text>
            </Group>
            
            <Card withBorder p="md">
              <ResultsCard results={selectedBacktest.results} />
            </Card>

            {selectedBacktest.parameters && (
              <Card withBorder p="md">
                <Group mb="sm">
                  <IconSettings size={16} />
                  <Text fw={500}>Paramètres utilisés</Text>
                </Group>
                <Text size="sm" c="dimmed">
                  RSI: {selectedBacktest.parameters.rsi_period} | 
                  SMA: {selectedBacktest.parameters.sma_period} | 
                  TP: {selectedBacktest.parameters.tp} | 
                  SL: {selectedBacktest.parameters.sl}
                </Text>
              </Card>
            )}
          </Stack>
        )}
      </Modal>
    </Stack>
  );
};

export default BacktestingPage;
