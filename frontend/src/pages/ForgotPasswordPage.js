import React, { useState } from 'react';
import { Container, Paper, Title, TextInput, Button, Text, Alert, Group, Anchor } from '@mantine/core';
import { useForm } from '@mantine/form';
import { notifications } from '@mantine/notifications';
import { IconMail, IconCheck, IconX } from '@tabler/icons-react';
import { Link } from 'react-router-dom';
import api from '../services/api';

function ForgotPasswordPage() {
  const [loading, setLoading] = useState(false);
  const [emailSent, setEmailSent] = useState(false);

  const form = useForm({
    initialValues: {
      email: '',
    },
    validate: {
      email: (value) => (/^\S+@\S+$/.test(value) ? null : 'Email invalide'),
    },
  });

  const handleSubmit = async (values) => {
    setLoading(true);
    try {
      await api.post('/password-reset/', values);
      setEmailSent(true);
      notifications.show({
        title: 'Email envoyé',
        message: 'Vérifiez votre boîte mail pour réinitialiser votre mot de passe',
        color: 'green',
        icon: <IconCheck size={16} />,
      });
    } catch (error) {
      notifications.show({
        title: 'Erreur',
        message: 'Une erreur est survenue. Veuillez réessayer.',
        color: 'red',
        icon: <IconX size={16} />,
      });
    } finally {
      setLoading(false);
    }
  };

  if (emailSent) {
    return (
      <Container size={420} my={40}>
        <Paper withBorder shadow="md" p={30} mt={30} radius="md">
          <Title ta="center" mb="md">
            Email envoyé
          </Title>
          <Alert color="green" icon={<IconCheck size={16} />} mb="md">
            Un email de réinitialisation a été envoyé à votre adresse email.
            Cliquez sur le lien dans l'email pour réinitialiser votre mot de passe.
          </Alert>
          <Group justify="center" mt="lg">
            <Anchor component={Link} to="/login" size="sm">
              Retour à la connexion
            </Anchor>
          </Group>
        </Paper>
      </Container>
    );
  }

  return (
    <Container size={420} my={40}>
      <Paper withBorder shadow="md" p={30} mt={30} radius="md">
        <Title ta="center" mb="md">
          Mot de passe oublié
        </Title>
        <Text c="dimmed" size="sm" ta="center" mb="md">
          Entrez votre adresse email pour recevoir un lien de réinitialisation
        </Text>

        <form onSubmit={form.onSubmit(handleSubmit)}>
          <TextInput
            label="Email"
            placeholder="votre@email.com"
            required
            leftSection={<IconMail size={16} />}
            {...form.getInputProps('email')}
          />

          <Button
            type="submit"
            fullWidth
            mt="xl"
            loading={loading}
          >
            Envoyer le lien de réinitialisation
          </Button>
        </form>

        <Group justify="center" mt="lg">
          <Anchor component={Link} to="/login" size="sm">
            Retour à la connexion
          </Anchor>
        </Group>
      </Paper>
    </Container>
  );
}

export default ForgotPasswordPage;
