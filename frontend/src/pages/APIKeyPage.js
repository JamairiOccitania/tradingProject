import React, { useState, useEffect } from 'react';
import {
  Stack,
  Title,
  Text,
  Card,
  TextInput,
  PasswordInput,
  Button,
  Group,
  Alert,
  Loader,
  Center,
  Badge,
  Divider
} from '@mantine/core';
import {
  IconKey,
  IconShield,
  IconAlertTriangle,
  IconCheck,
  IconInfoCircle
} from '@tabler/icons-react';
import { useForm } from '@mantine/form';
import { notifications } from '@mantine/notifications';
import api from '../services/api';

function APIKeyPage() {
  const [currentKey, setCurrentKey] = useState(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  const form = useForm({
    initialValues: {
      oanda_api_key: '',
      oanda_account_id: ''
    },
    validate: {
      oanda_api_key: (value) => 
        value.length < 10 ? 'La clé API doit contenir au moins 10 caractères' : null,
      oanda_account_id: (value) => 
        value.length < 5 ? 'L\'ID de compte doit contenir au moins 5 caractères' : null,
    }
  });

  useEffect(() => {
    fetchApiKey();
  }, []);

  const fetchApiKey = async () => {
    try {
      const response = await api.get('/keys/');
      if (response.data.length > 0) {
        const key = response.data[0];
        setCurrentKey(key);
        form.setValues({
          oanda_api_key: key.oanda_api_key || '',
          oanda_account_id: key.oanda_account_id || ''
        });
      }
    } catch (error) {
      console.error('Erreur lors du chargement de la clé API', error);
      notifications.show({
        title: 'Erreur',
        message: 'Impossible de charger la clé API',
        color: 'red',
      });
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (values) => {
    setSaving(true);
    try {
      const data = { 
        oanda_api_key: values.oanda_api_key,
        oanda_account_id: values.oanda_account_id 
      };

      if (currentKey) {
        await api.put(`/keys/${currentKey.id}/`, data);
        notifications.show({
          title: 'Clé API mise à jour',
          message: 'Votre clé API OANDA a été mise à jour avec succès',
          color: 'green',
        });
      } else {
        await api.post('/keys/', data);
        notifications.show({
          title: 'Clé API ajoutée',
          message: 'Votre clé API OANDA a été ajoutée avec succès',
          color: 'green',
        });
      }

      form.reset();
      fetchApiKey();
    } catch (error) {
      console.error('Erreur lors de la sauvegarde de la clé API', error);
      notifications.show({
        title: 'Erreur',
        message: 'Impossible de sauvegarder la clé API',
        color: 'red',
      });
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async () => {
    if (!currentKey) return;

    try {
      await api.delete(`/keys/${currentKey.id}/`);
      notifications.show({
        title: 'Clé API supprimée',
        message: 'Votre clé API a été supprimée avec succès',
        color: 'orange',
      });
      setCurrentKey(null);
    } catch (error) {
      notifications.show({
        title: 'Erreur',
        message: 'Impossible de supprimer la clé API',
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
        <Title order={1}>Gestion de la Clé API OANDA</Title>
        <Text c="dimmed">
          Configurez votre clé API OANDA pour permettre au trading automatisé
        </Text>
      </div>

      {/* Statut actuel */}
      <Card withBorder p="lg">
        <Group justify="space-between" mb="md">
          <Text fw={600} size="lg">Statut de la configuration</Text>
          {currentKey ? (
            <Badge color="green" variant="light" leftSection={<IconCheck size={12} />}>
              Configurée
            </Badge>
          ) : (
            <Badge color="red" variant="light" leftSection={<IconAlertTriangle size={12} />}>
              Non configurée
            </Badge>
          )}
        </Group>

        {currentKey ? (
          <Stack gap="sm">
            <Text c="dimmed">
              Une clé API est configurée pour le compte : <Text span fw={500}>{currentKey.oanda_account_id}</Text>
            </Text>
            <Text size="sm" c="dimmed">
              Configurée le : {new Date(currentKey.created_at).toLocaleDateString('fr-FR')}
            </Text>
          </Stack>
        ) : (
          <Text c="dimmed">
            Aucune clé API n'est configurée. Ajoutez votre clé OANDA ci-dessous.
          </Text>
        )}
      </Card>

      {/* Informations de sécurité */}
      <Alert
        icon={<IconShield size={16} />}
        title="Sécurité"
        color="blue"
        variant="light"
      >
        <Stack gap="xs">
          <Text size="sm">
            • Votre clé API est chiffrée avant d'être stockée en base de données
          </Text>
          <Text size="sm">
            • Seules les opérations autorisées par OANDA sont possibles
          </Text>
          <Text size="sm">
            • Vous pouvez révoquer l'accès à tout moment depuis votre compte OANDA
          </Text>
        </Stack>
      </Alert>

      {/* Formulaire */}
      <Card withBorder p="lg">
        <Stack gap="md">
          <Group>
            <IconKey size={20} />
            <Text fw={600} size="lg">
              {currentKey ? 'Mettre à jour' : 'Ajouter'} la clé API
            </Text>
          </Group>

          <form onSubmit={form.onSubmit(handleSubmit)}>
            <Stack gap="md">
              <TextInput
                label="ID de compte OANDA"
                placeholder="123-456-7890123-001"
                description="L'identifiant de votre compte OANDA (trouvable dans votre dashboard OANDA)"
                required
                {...form.getInputProps('oanda_account_id')}
              />

              <PasswordInput
                label="Clé API OANDA"
                placeholder="Votre clé API OANDA"
                description="Votre clé API privée (sera chiffrée avant stockage)"
                required
                {...form.getInputProps('oanda_api_key')}
              />

              <Group justify="flex-end" mt="md">
                {currentKey && (
                  <Button
                    variant="light"
                    color="red"
                    onClick={handleDelete}
                  >
                    Supprimer
                  </Button>
                )}
                <Button
                  type="submit"
                  loading={saving}
                  leftSection={<IconKey size={16} />}
                >
                  {currentKey ? 'Mettre à jour' : 'Ajouter'} la clé
                </Button>
              </Group>
            </Stack>
          </form>
        </Stack>
      </Card>

      {/* Instructions */}
      <Card withBorder p="lg">
        <Stack gap="md">
          <Group>
            <IconInfoCircle size={20} />
            <Text fw={600} size="lg">Comment obtenir votre clé API OANDA</Text>
          </Group>

          <Divider />

          <Stack gap="sm">
            <Text fw={500}>1. Connectez-vous à votre compte OANDA</Text>
            <Text size="sm" c="dimmed" pl="md">
              Rendez-vous sur le portail développeur OANDA
            </Text>

            <Text fw={500}>2. Générez une clé API</Text>
            <Text size="sm" c="dimmed" pl="md">
              Créez une nouvelle clé API avec les permissions de trading
            </Text>

            <Text fw={500}>3. Copiez votre clé et ID de compte</Text>
            <Text size="sm" c="dimmed" pl="md">
              Notez bien votre clé API et l'ID de votre compte
            </Text>

            <Text fw={500}>4. Configurez dans cette interface</Text>
            <Text size="sm" c="dimmed" pl="md">
              Collez vos informations dans le formulaire ci-dessus
            </Text>
          </Stack>
        </Stack>
      </Card>
    </Stack>
  );
}

export default APIKeyPage;
