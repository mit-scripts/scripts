{-# LANGUAGE ViewPatterns #-}

-- POSIX only

import Prelude hiding (catch)

import Data.Char
import Data.List
import Data.Maybe

import Control.Arrow
import Control.Monad
import Control.Applicative
import Control.Concurrent
import Control.Concurrent.MVar
import Control.Concurrent.STM
import Control.Exception

import System.FilePath
import System.Process
import System.IO
import System.Directory
import System.Exit
import System.Posix hiding (createDirectory)

destdir = "/mit/scripts/sec-tools/store/versions"

whenM :: Monad m => m Bool -> m () -> m ()
whenM p x = p >>= \b -> if b then x else return ()

-- A simple semaphore implementation on a TVar Int.  Don't recursively
-- call this while in a limit; you will be sad.
limit :: TVar Int -> IO a -> IO a
limit pool m = do
    atomically $ do
        i <- readTVar pool
        check (i > 0)
        writeTVar pool (i - 1)
    m `finally` atomically (readTVar pool >>= writeTVar pool . (+1))

-- These are cribbed off http://www.haskell.org/ghc/docs/5.00/set/sec-ghc-concurrency.html
-- but with less unsafePerformIO

-- Fork and register a child, so that it can be waited on
forkChild :: MVar [MVar ()] -> IO () -> IO ()
forkChild children m = do
    c <- newEmptyMVar
    forkIO (m `finally` putMVar c ())
    cs <- takeMVar children
    putMVar children (c:cs)

-- Wait on all children
waitForChildren :: MVar [MVar ()] -> IO ()
waitForChildren children = do
    cs' <- takeMVar children
    case cs' of
        [] -> return ()
        (c:cs) -> do
            putMVar children cs
            takeMVar c
            waitForChildren children

-- Check if we have permissions
checkPerm :: TVar Int -> FilePath -> IO Bool
checkPerm pool base = ("system:scripts-security-upd rlidwk" `isInfixOf`) <$> exec pool "fs" ["listacl", base]

newVersion pool cn base = do
    stdout <- exec pool "sudo" ["-u", cn, "git", "--git-dir", base </> ".git", "describe", "--tags", "--always"]
    -- XXX null stdout is an error condition, should say something
    return (if null stdout then stdout else init stdout) -- munge off trailing newline
oldVersion base =
    -- XXX empty file is an error condition, should say something
    last . lines <$> readFile (base </> ".scripts-version")

writeOut handle_mvar base r =
    withMVar handle_mvar $ \handle -> do
        let line = base ++ ":" ++ r ++ "\n"
        putStr line
        hPutStr handle line

exec :: TVar Int -> String -> [String] -> IO String
exec pool bin args = do
    (_, stdout, _) <- limit pool $ readProcessWithExitCode bin args ""
    return stdout

main = do
    let lockfile = destdir ++ ".lock"
    (_, host, _) <- readProcessWithExitCode "hostname" [] ""
    pid <- getProcessID
    whenM (doesFileExist lockfile) (error "Another parallel-find already in progress")
    -- XXX if we lose the race the error message isn't as good
    bracket_ (openFd lockfile WriteOnly (Just 0o644) (defaultFileFlags {exclusive = True})
                >>= fdToHandle
                >>= \h -> hPutStrLn h (host ++ " " ++ show pid) >> hClose h)
             (removeFile lockfile)
             (prepare >> parfind)

prepare = do
    whenM (doesDirectoryExist destdir) $ do
        uniq <- show <$> epochTime
        -- XXX does the wrong thing if you lose the race
        renameDirectory destdir (destdir ++ uniq)
    createDirectory destdir

parfind = do
    findpool <- newTVarIO 50
    pool <- newTVarIO 10 -- git/fs gets its own pool so they don't starve
    children <- newMVar []
    userlines <- lines <$> readFile "/mit/scripts/admin/backup/userlist"
    let userdirs = filter ((/= "dn:") . fst) -- XXX should be done by generator of userlist
                 . catMaybes
                 . map (\s -> second tail    -- proof obligation discharged by elemIndex
                           .  (`splitAt` s)
                          <$> elemIndex ' ' s)
                 $  userlines
    forM_ userdirs $ \(cn, homedir) -> forkChild children $ do
        subchildren <- newMVar []
        let scriptsdir = homedir </> "web_scripts"
        matches <- lines <$> exec findpool "find" [scriptsdir, "-xdev", "-name", ".scripts-version", "-o", "-name", ".scripts"]
        withFile (destdir </> cn) WriteMode $ \h -> do
            mh <- newMVar h
            forM_ matches $ \dir -> forkChild subchildren . handle (\(SomeException e) -> putStrLn (dir ++ ": " ++ show e)) $ do
                let base = takeDirectory dir
                whenM (checkPerm pool base) $ do
                if ".scripts" `isSuffixOf` dir
                    then newVersion pool cn base >>= writeOut mh base
                    else whenM (not <$> doesDirectoryExist (base </> ".scripts")) $ oldVersion base >>= writeOut mh base
            waitForChildren subchildren
    waitForChildren children
