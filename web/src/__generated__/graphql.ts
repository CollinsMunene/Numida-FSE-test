/* eslint-disable */
import { TypedDocumentNode as DocumentNode } from '@graphql-typed-document-node/core';
export type Maybe<T> = T | null;
export type InputMaybe<T> = Maybe<T>;
export type Exact<T extends { [key: string]: unknown }> = { [K in keyof T]: T[K] };
export type MakeOptional<T, K extends keyof T> = Omit<T, K> & { [SubKey in K]?: Maybe<T[SubKey]> };
export type MakeMaybe<T, K extends keyof T> = Omit<T, K> & { [SubKey in K]: Maybe<T[SubKey]> };
export type MakeEmpty<T extends { [key: string]: unknown }, K extends keyof T> = { [_ in K]?: never };
export type Incremental<T> = T | { [P in keyof T]?: P extends ' $fragmentName' | '__typename' ? T[P] : never };
/** All built-in and custom scalars, mapped to their actual values */
export type Scalars = {
  ID: { input: string; output: string; }
  String: { input: string; output: string; }
  Boolean: { input: boolean; output: boolean; }
  Int: { input: number; output: number; }
  Float: { input: number; output: number; }
  Date: { input: any; output: any; }
};

export type Loan = {
  __typename?: 'Loan';
  due_date: Scalars['Date']['output'];
  id: Scalars['Int']['output'];
  interest_rate: Scalars['Float']['output'];
  name: Scalars['String']['output'];
  payment_date?: Maybe<Scalars['Date']['output']>;
  payments?: Maybe<Array<LoanPayment>>;
  principal: Scalars['Int']['output'];
  status?: Maybe<Scalars['String']['output']>;
};

export type LoanFilter = {
  due_date?: InputMaybe<Scalars['Date']['input']>;
  id?: InputMaybe<Scalars['Int']['input']>;
  name?: InputMaybe<Scalars['String']['input']>;
};

export type LoanPayment = {
  __typename?: 'LoanPayment';
  amount: Scalars['Float']['output'];
  id: Scalars['Int']['output'];
  loan?: Maybe<Loan>;
  loan_id: Scalars['Int']['output'];
  payment_date: Scalars['Date']['output'];
  status: Scalars['String']['output'];
};

export type LoanPaymentFilter = {
  id?: InputMaybe<Scalars['Int']['input']>;
  loan_id?: InputMaybe<Scalars['Int']['input']>;
  status?: InputMaybe<Scalars['String']['input']>;
};

export type Mutation = {
  __typename?: 'Mutation';
  deleteLoan: Scalars['Boolean']['output'];
  updateLoan: Loan;
};


export type MutationDeleteLoanArgs = {
  loan_id: Scalars['Int']['input'];
};


export type MutationUpdateLoanArgs = {
  loan_id: Scalars['Int']['input'];
};

export type Query = {
  __typename?: 'Query';
  loanPayments: Array<LoanPayment>;
  loans: Array<Loan>;
};


export type QueryLoanPaymentsArgs = {
  filters?: InputMaybe<LoanPaymentFilter>;
};


export type QueryLoansArgs = {
  filters?: InputMaybe<LoanFilter>;
  isCombined: Scalars['Boolean']['input'];
};

export type LoanPaymentsQueryVariables = Exact<{
  filters?: InputMaybe<LoanPaymentFilter>;
}>;


export type LoanPaymentsQuery = { __typename?: 'Query', loanPayments: Array<{ __typename?: 'LoanPayment', id: number, payment_date: any, amount: number, status: string, loan?: { __typename?: 'Loan', interest_rate: number, principal: number, due_date: any } | null }> };


export const LoanPaymentsDocument = {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"query","name":{"kind":"Name","value":"loanPayments"},"variableDefinitions":[{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"filters"}},"type":{"kind":"NamedType","name":{"kind":"Name","value":"LoanPaymentFilter"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"loanPayments"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"filters"},"value":{"kind":"Variable","name":{"kind":"Name","value":"filters"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"payment_date"}},{"kind":"Field","name":{"kind":"Name","value":"amount"}},{"kind":"Field","name":{"kind":"Name","value":"status"}},{"kind":"Field","name":{"kind":"Name","value":"loan"},"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"interest_rate"}},{"kind":"Field","name":{"kind":"Name","value":"principal"}},{"kind":"Field","name":{"kind":"Name","value":"due_date"}}]}}]}}]}}]} as unknown as DocumentNode<LoanPaymentsQuery, LoanPaymentsQueryVariables>;