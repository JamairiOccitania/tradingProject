import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Paper,
  TextInput,
  PasswordInput,
  Button,
  Title,
  Text,
  Container,
  Center,
  Stack,
  Alert,
  Anchor,
  Group
} from '@mantine/core';
import { IconLogin, IconAlertCircle } from '@tabler/icons-react';
import { notifications } from '@mantine/notifications';
import { Link } from 'react-router-dom';
import api from '../services/api';

function LoginPage() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const response = await api.post('/login/', { username, password });
      localStorage.setItem('access_token', response.data.access);
      localStorage.setItem('refresh_token', response.data.refresh);
      
      notifications.show({
        title: 'Connexion réussie',
        message: 'Bienvenue sur la plateforme de trading !',
        color: 'green',
      });
      
      navigate('/dashboard');
    } catch (error) {
      console.error('Login failed', error);
      setError('Nom d\'utilisateur ou mot de passe incorrect');
      notifications.show({
        title: 'Erreur de connexion',
        message: 'Vérifiez vos identifiants et réessayez',
        color: 'red',
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <Container size={420} my={40}>
      <Center>
        <Stack align="center" gap="lg">
          <Title order={1} ta="center" c="blue">
            Trading Platform
          </Title>
          <Text c="dimmed" size="sm" ta="center">
            Connectez-vous pour accéder à votre tableau de bord
          </Text>
        </Stack>
      </Center>

      <Paper withBorder shadow="md" p={30} mt={30} radius="md">
        <form onSubmit={handleSubmit}>
          <Stack gap="md">
            {error && (
              <Alert
                icon={<IconAlertCircle size={16} />}
                color="red"
                variant="light"
              >
                {error}
              </Alert>
            )}

            <TextInput
              label="Nom d'utilisateur"
              placeholder="Votre nom d'utilisateur"
              required
              value={username}
              onChange={(e) => setUsername(e.target.value)}
            />

            <PasswordInput
              label="Mot de passe"
              placeholder="Votre mot de passe"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />

            <Button
              type="submit"
              fullWidth
              mt="xl"
              loading={loading}
              leftSection={<IconLogin size={16} />}
            >
              Se connecter
            </Button>

            <Group justify="center" mt="md">
              <Anchor component={Link} to="/forgot-password" size="sm">
                Mot de passe oublié ?
              </Anchor>
            </Group>
          </Stack>
        </form>
      </Paper>
    </Container>
  );
}

export default LoginPage;
