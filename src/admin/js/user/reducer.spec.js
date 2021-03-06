import { expect } from 'chai';
import sinon from 'sinon';
import reducerFactory, { isAuthenticated } from './reducer';
import { signIn, signOut, signUp } from './actions';

describe('user reducer', () => {
    const getItemWithUser = sinon.stub();
    const expireTokenTime = new Date(Date.now() + (30 * 1000));
    getItemWithUser.withArgs('id').returns('foo');
    getItemWithUser.withArgs('email').returns('foo@bar.com');
    getItemWithUser.withArgs('token').returns('bar');
    getItemWithUser.withArgs('expires').returns(expireTokenTime.getTime() / 1000);

    const localStorageWithUser = {
        getItem: getItemWithUser,
    };

    it('should return the user saved in localStorage as its initial state', () => {
        const reducer = reducerFactory(localStorageWithUser);

        expect(reducer(undefined, { type: 'foo' })).to.deep.equal({
            authenticated: true,
            email: 'foo@bar.com',
            id: 'foo',
            loading: false,
            token: 'bar',
            expires: expireTokenTime,
        });
    });

    it('should handle the signIn.success action', () => {
        const getItem = sinon.stub().returns(undefined);
        const localStorage = {
            getItem,
        };
        const reducer = reducerFactory(localStorage);

        expect(reducer(undefined, signIn.success({
            email: 'foo@bar.com',
            id: 'foo',
            token: 'bar',
            expires: expireTokenTime,
        }))).to.deep.equal({
            authenticated: true,
            error: false,
            id: 'foo',
            email: 'foo@bar.com',
            loading: false,
            token: 'bar',
            expires: expireTokenTime,
        });
    });

    it('should handle the signOut.success action', () => {
        const reducer = reducerFactory(localStorageWithUser);

        expect(reducer(undefined, signOut.success())).to.deep.equal({
            authenticated: false,
            id: null,
            email: null,
            loading: false,
            token: null,
            expires: null,
        });
    });

    describe('isAuthenticated', () => {
        it('should return false if state.user.authenticated is false', () => {
            expect(isAuthenticated({ user: { authenticated: false } })).to.be.false;
        });

        it('should return false if state.user.expires is anterior to now', () => {
            const expires = new Date(Date.now() - 1000);
            expect(isAuthenticated({ user: { authenticated: true, expires } })).to.be.false;
        });

        it('should return true if state.user.expires is posterior to now', () => {
            const expires = new Date(Date.now() + 1000);
            expect(isAuthenticated({ user: { authenticated: true, expires } })).to.be.true;
        });
    });
});
