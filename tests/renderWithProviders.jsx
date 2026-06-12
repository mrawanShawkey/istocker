import React from "react";
import { render } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { AppProvider } from "../context/AppContext";
import { userStorage } from "../services/storageService";
import Toast from "../components/ui/Toast";

/**
 * renderWithProviders(ui, options)
 *
 * options:
 *   initialEntries  – array of routes for MemoryRouter (default: ['/'])
 *   userOverride    – user object to pre-load into localStorage before render
 *                     (null = explicitly no user, undefined = leave as-is)
 */
export const renderWithProviders = (ui, options = {}) => {
  const {
    initialEntries = ["/"],
    userOverride,
    ...renderOptions
  } = options;

  // Set the user in localStorage BEFORE rendering so AppProvider
  // reads it immediately via its useState initializer.
  if (userOverride !== undefined) {
    if (userOverride === null) {
      userStorage.remove();
    } else {
      userStorage.set(userOverride);
    }
  }

  return render(
    <AppProvider>
      <Toast />
      <MemoryRouter initialEntries={initialEntries}>
        {ui}
      </MemoryRouter>
    </AppProvider>,
    renderOptions
  );
};